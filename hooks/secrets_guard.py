import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Patterns that indicate hardcoded Supabase credentials in source code.
# Each tuple: (regex, human-readable label).
# st.secrets["KEY"] usage never matches these patterns — no false positives.
PATTERNS = [
    (r'SUPABASE_URL\s*=\s*["\']https://', "SUPABASE_URL 하드코딩"),
    (r'SUPABASE_KEY\s*=\s*["\']eyJ', "SUPABASE_KEY 하드코딩"),
    (r'create_client\s*\(\s*["\']https://[^"\']*supabase', "create_client()에 Supabase URL 직접 입력"),
]

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

if not path or not path.endswith(".py") or not Path(path).exists():
    sys.exit(0)

try:
    content = Path(path).read_text(encoding="utf-8", errors="replace")
except OSError:
    sys.exit(0)

violations = []
for pattern, label in PATTERNS:
    for m in re.finditer(pattern, content):
        line_no = content[: m.start()].count("\n") + 1
        violations.append(f"  - line {line_no}: {label}")

if not violations:
    sys.exit(0)

name = Path(path).name
msg = "\n".join([
    f"[보안 차단] {name}에 Supabase 인증 정보가 코드에 직접 작성되어 있습니다.",
    "",
    *violations,
    "",
    "수정 방법:",
    "  1. 해당 값을 .streamlit/secrets.toml로 이동",
    "  2. 코드에서 st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY']로 참조",
    "  3. db.py get_client() 패턴 참고 (TASK-005)",
])

print(json.dumps({
    "decision": "block",
    "reason": msg,
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": msg,
    },
}, ensure_ascii=False))
