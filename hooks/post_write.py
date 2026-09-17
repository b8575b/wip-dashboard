import json
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).parent.parent

MAX_LINES = {"app.py": 300, "backlog_cli.py": 550, "db.py": 100}
DEFAULT_MAX, HOOKS_MAX = 150, 100


def get_max(path: str) -> int:
    p = Path(path)
    if "hooks" in p.parts:
        return HOOKS_MAX
    return MAX_LINES.get(p.name, DEFAULT_MAX)


def sh(cmd: list, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def check_py(path: str) -> None:
    if not path.endswith(".py") or not Path(path).exists():
        return

    msgs, blocking = [], False

    lines = len(Path(path).read_text(encoding="utf-8").splitlines())
    mx = get_max(path)
    pct = lines / mx * 100
    name = Path(path).name
    if pct >= 100:
        msgs.append(f"[코드 길이 초과] {name}: {lines}/{mx}줄 ({pct:.0f}%) — 파일을 분리하거나 코드를 줄여서 다시 작업하세요.")
        blocking = True
    elif pct >= 85:
        msgs.append(f"[코드 길이 경고] {name}: {lines}/{mx}줄 ({pct:.0f}%) — 85% 초과")

    r = sh([sys.executable, "-m", "py_compile", path])
    if r.returncode != 0:
        msgs.append(f"[구문 오류] 수정 후 다시 작업하세요:\n{r.stderr.strip()}")
        blocking = True

    r = sh([sys.executable, "-m", "flake8", "--max-line-length=100",
            "--extend-ignore=W503,E303", path])
    if r.returncode != 0 and "No module named" not in r.stderr:
        msgs.append(f"[Lint 오류] 수정 후 다시 작업하세요:\n{r.stdout.strip()}")
        blocking = True

    if not msgs:
        return

    combined = "\n\n".join(msgs)
    out = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": combined}}
    if blocking:
        out["decision"] = "block"
        out["reason"] = combined
    print(json.dumps(out, ensure_ascii=False))


def handle_backlog(path: str) -> None:
    if "backlog.json" not in path:
        return

    diff = sh(["git", "diff", "HEAD", "--", "backlog.json"], cwd=PROJECT_DIR)
    added = [ln[1:] for ln in (diff.stdout or "").splitlines() if ln.startswith("+")]
    is_done = any('"status": "done"' in ln for ln in added)

    sh(["git", "add", "backlog.json"], cwd=PROJECT_DIR)

    if is_done:
        try:
            tasks = json.loads(Path(path).read_text(encoding="utf-8"))["tasks"]
            done = [t["title"] for t in tasks if t["status"] == "done"]
            summary = ", ".join(done[:2]) + (f" 외 {len(done)-2}건" if len(done) > 2 else "")
        except Exception:
            summary = "task 완료"
        sh(["git", "add", "-A"], cwd=PROJECT_DIR)
        r = sh(["git", "commit", "-m", f"feat: complete - {summary} [auto]"], cwd=PROJECT_DIR)
        if r.returncode == 0:
            pr = sh(["git", "push"], cwd=PROJECT_DIR)
            label = "commit + push 완료" if pr.returncode == 0 else "commit 완료 (push 실패)"
            print(json.dumps({"systemMessage": f"[Backlog] Task 완료 → {label}: {summary}"}))
    else:
        r = sh(["git", "commit", "-m", "chore: update backlog [auto]"], cwd=PROJECT_DIR)
        if r.returncode == 0:
            print(json.dumps({"systemMessage": "[Backlog] 자동 commit 완료"}))


data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")
if path:
    check_py(path)
    handle_backlog(path)
