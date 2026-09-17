import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).parent.parent

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

if not re.search(r"\bgit\s+add\b", cmd):
    sys.exit(0)

# Case 1: secrets.toml explicitly named in the git add command → always block
if "secrets.toml" in cmd:
    msg = (
        "[보안 차단] .streamlit/secrets.toml을 직접 git add하려 했습니다.\n"
        "이 파일에는 Supabase API Key가 포함되어 절대 커밋하면 안 됩니다.\n\n"
        "수정 방법:\n"
        "  .gitignore에 '.streamlit/secrets.toml' 또는 '.streamlit/' 추가\n"
        "  이미 추적 중이라면: git rm --cached .streamlit/secrets.toml"
    )
    print(json.dumps({
        "systemMessage": msg,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        },
    }, ensure_ascii=False))
    sys.exit(0)

# Case 2: broad add (git add -A / git add .) when secrets.toml exists without gitignore coverage
broad = re.search(r"git\s+add\s+(-A|\.)\b", cmd) or re.search(r"git\s+add\s+--all\b", cmd)
secrets_path = PROJECT_DIR / ".streamlit" / "secrets.toml"

if not broad or not secrets_path.exists():
    sys.exit(0)

covered = False
gitignore = PROJECT_DIR / ".gitignore"
try:
    if gitignore.exists():
        for line in gitignore.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                if "secrets.toml" in stripped or ".streamlit" in stripped:
                    covered = True
                    break
except OSError:
    pass  # read failure → treat as not covered, warn

if covered:
    sys.exit(0)

warn_msg = (
    "[보안 경고] git add -A 실행 시 .streamlit/secrets.toml이 스테이징될 수 있습니다.\n"
    ".gitignore에 해당 파일이 등록되어 있지 않습니다.\n\n"
    "조치 후 재실행:\n"
    "  echo '.streamlit/secrets.toml' >> .gitignore"
)
print(json.dumps({
    "systemMessage": warn_msg,
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": warn_msg,
    },
}, ensure_ascii=False))
