import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

try:
    json.load(sys.stdin)
except Exception:
    pass

r = subprocess.run(
    ["git", "branch", "--show-current"],
    capture_output=True, text=True, cwd=PROJECT_DIR,
)

if r.returncode != 0:
    print(json.dumps({"systemMessage": "[브랜치] git 저장소가 초기화되지 않았습니다. TASK-001을 먼저 완료하세요."}))
    sys.exit(0)

branch = r.stdout.strip()

if not branch:
    sys.exit(0)

if branch == "main":
    user_msg = f"[브랜치] 현재: {branch} — main 브랜치에서 작업 중입니다. dev 브랜치로 전환하세요."
    claude_ctx = (
        "현재 브랜치가 main입니다. 개발 작업은 dev 브랜치에서 진행해야 합니다.\n"
        "사용자에게 다음 명령으로 전환하도록 안내하세요:\n"
        "  git checkout dev       # 기존 dev 브랜치로 전환\n"
        "  git checkout -b dev    # 새 dev 브랜치 생성 및 전환"
    )
    print(json.dumps({
        "systemMessage": user_msg,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": claude_ctx,
        },
    }))
else:
    print(json.dumps({"systemMessage": f"[브랜치] 현재: {branch}"}))
