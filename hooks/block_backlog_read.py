import json
import sys

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

if "backlog.json" not in path:
    sys.exit(0)

msg = "\n".join([
    "backlog.json은 직접 읽을 수 없습니다. CLI 툴을 사용하세요:",
    "",
    "  python backlog_cli.py list                           # 전체 목록",
    "  python backlog_cli.py list --status todo             # 상태 필터",
    "  python backlog_cli.py list --priority high           # 우선순위 필터",
    "  python backlog_cli.py show TASK-001                  # 상세 조회",
    "  python backlog_cli.py update TASK-001 --status done  # 상태 변경",
    "  python backlog_cli.py add                            # 새 태스크 추가",
    "  python backlog_cli.py open TASK-001                  # 상세 문서 열기",
])

print(json.dumps({
    "systemMessage": msg,
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": msg,
    },
}, ensure_ascii=False))
