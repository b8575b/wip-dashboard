import json
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).parent.parent
PROC_TIMEOUT = 25  # 내부 프로세스 timeout (초); settings의 hook timeout=60보다 짧아야 함
MAX_LINES = {"app.py": 300, "backlog_cli.py": 550, "db.py": 100}
HOOKS_MAX, DEFAULT_MAX = 100, 150


def get_max(p: Path) -> int:
    return HOOKS_MAX if "hooks" in p.parts else MAX_LINES.get(p.name, DEFAULT_MAX)


def collect_py() -> list:
    skip = {".venv", "venv", "__pycache__", ".git", "site-packages"}
    return sorted(
        p for p in PROJECT_DIR.rglob("*.py")
        if not any(s in p.parts for s in skip)
        and not p.name.startswith("_test_")
    )


try:
    data = json.load(sys.stdin)
    re_entry = data.get("stop_hook_active", False)
except Exception:
    re_entry = False

py_files = collect_py()
failures = []

# 1. 줄수 검사
for f in py_files:
    try:
        n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        continue
    mx = get_max(f)
    if n >= mx:
        rel = f.relative_to(PROJECT_DIR)
        failures.append(f"[길이 초과] {rel}: {n}/{mx}줄")

# 2. Lint + Syntax (build 등가 검사)
# 이 프로젝트는 별도 빌드 단계 없음 (Streamlit interpreted Python).
# E999=구문 오류, E/W/F=스타일. 타임아웃은 미검증(실패)으로 기록.
if py_files:
    try:
        r = subprocess.run(
            [sys.executable, "-m", "flake8", "--max-line-length=100",
             "--extend-ignore=W503,E303"] + [str(f) for f in py_files],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=PROC_TIMEOUT, cwd=PROJECT_DIR,
        )
        if r.returncode != 0 and "No module named" not in r.stderr:
            failures.append(f"[Lint/Syntax]\n{r.stdout.strip()}")
    except subprocess.TimeoutExpired:
        failures.append(
            f"[시간 초과] flake8 {PROC_TIMEOUT}s 초과 — 미검증 (완료 근거 불가)"
        )

if not failures:
    sys.exit(0)

msg = f"[Stop Check] 미통과 {len(failures)}건 — 수정 후 재제출\n\n" + "\n\n".join(failures)

if re_entry:
    # 재진입: 무한 반복 방지를 위해 차단하지 않음.
    # 단, 미통과 항목을 명시적으로 보고해 완료 처리하지 않도록 함.
    print(json.dumps({"systemMessage": f"[재진입 감지] {msg}"}, ensure_ascii=False))
    sys.exit(0)

print(json.dumps({
    "decision": "block",
    "reason": msg,
    "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": msg},
}, ensure_ascii=False))
sys.stderr.write(f"\n{msg}\n\n수정 방법: 위 항목을 수정한 뒤 다시 제출하세요.\n")
sys.exit(2)
