#!/usr/bin/env python3
"""WIP 재공 현황판 Backlog CLI

Commands:
  list    태스크 목록 조회 (필터 지원)
  show    태스크 상세 조회
  add     새 태스크 추가 (대화형)
  update  태스크 필드 수정
  open    상세 문서(.md) 열기
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Windows 터미널 UTF-8 강제 설정
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("rich 패키지가 필요합니다: pip install rich")
    sys.exit(1)

BACKLOG_PATH = Path(__file__).parent / "backlog.json"
TASKS_DIR = Path(__file__).parent / "tasks"

console = Console()

VALID_STATUSES = [
    "todo",
    "in_progress",
    "review",
    "pending_decision",
    "done",
    "cancelled",
    "waiting",
]
VALID_PRIORITIES = ["high", "medium", "low"]

STATUS_LABEL = {
    "todo": "할 일",
    "in_progress": "작업중",
    "review": "리뷰 필요",
    "pending_decision": "판단 필요",
    "done": "완료",
    "cancelled": "취소",
    "waiting": "대기",
}

STATUS_STYLE = {
    "todo": "white",
    "in_progress": "bold yellow",
    "review": "bold cyan",
    "pending_decision": "bold magenta",
    "done": "bold green",
    "cancelled": "dim",
    "waiting": "bold blue",
}

STATUS_EMOJI = {
    "todo": "[ ]",
    "in_progress": "[>]",
    "review": "[?]",
    "pending_decision": "[!]",
    "done": "[v]",
    "cancelled": "[x]",
    "waiting": "[-]",
}

PRIORITY_STYLE = {
    "high": "bold red",
    "medium": "yellow",
    "low": "green",
}


# ── I/O helpers ───────────────────────────────────────────────────────────────


def load_backlog() -> dict:
    if not BACKLOG_PATH.exists():
        console.print(f"[red]backlog.json을 찾을 수 없습니다: {BACKLOG_PATH}[/red]")
        sys.exit(1)
    with open(BACKLOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_backlog(data: dict) -> None:
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_task(data: dict, task_id: str) -> dict | None:
    task_id = task_id.upper()
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def next_task_id(data: dict) -> str:
    ids = [t["id"] for t in data["tasks"] if t["id"].startswith("TASK-")]
    if not ids:
        return "TASK-001"
    numbers = [int(i.split("-")[1]) for i in ids]
    return f"TASK-{max(numbers) + 1:03d}"


def status_text(status: str) -> Text:
    emoji = STATUS_EMOJI.get(status, "")
    label = STATUS_LABEL.get(status, status)
    return Text(f"{emoji} {label}", style=STATUS_STYLE.get(status, ""))


def priority_text(priority: str) -> Text:
    return Text(priority, style=PRIORITY_STYLE.get(priority, ""))


# ── list ──────────────────────────────────────────────────────────────────────


def cmd_list(args) -> None:
    data = load_backlog()
    tasks = data["tasks"]

    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]
    if args.tag:
        tasks = [t for t in tasks if args.tag in t.get("tags", [])]

    if not tasks:
        console.print("[yellow]조건에 맞는 태스크가 없습니다.[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_lines=True, header_style="bold")
    table.add_column("ID", style="bold cyan", width=10, no_wrap=True)
    table.add_column("상태", width=13, no_wrap=True)
    table.add_column("P", width=6, no_wrap=True)
    table.add_column("제목", min_width=32)
    table.add_column("시간", width=5, justify="right")
    table.add_column("의존", width=22)
    table.add_column("담당자", width=8)

    for task in tasks:
        deps = ", ".join(task.get("dependencies", [])) or "-"
        assignee = task.get("assignee") or "-"
        est = f"{task['estimated_minutes']}m"

        table.add_row(
            task["id"],
            status_text(task["status"]),
            priority_text(task["priority"]),
            task["title"],
            est,
            deps,
            assignee,
        )

    total = len(data["tasks"])
    filtered = len(tasks)
    header = "[bold]WIP 재공 현황판 Backlog[/bold]"
    if filtered < total:
        header += f"  [dim]{filtered}/{total}건[/dim]"
    else:
        header += f"  [dim]총 {total}건[/dim]"

    console.print(f"\n{header}\n")
    console.print(table)

    # 상태별 요약 (전체 기준)
    counts = Counter(t["status"] for t in data["tasks"])
    parts = []
    for s in VALID_STATUSES:
        if counts[s]:
            label = STATUS_LABEL[s]
            st = STATUS_STYLE[s]
            parts.append(f"[{st}]{STATUS_EMOJI[s]} {label} {counts[s]}[/{st}]")
    console.print("  " + "   ".join(parts) + "\n")


# ── show ──────────────────────────────────────────────────────────────────────


def cmd_show(args) -> None:
    data = load_backlog()
    task = get_task(data, args.id)
    if not task:
        console.print(f"[red]'{args.id}' 태스크를 찾을 수 없습니다.[/red]")
        sys.exit(1)

    s = task["status"]
    p = task["priority"]
    s_style = STATUS_STYLE.get(s, "")
    p_style = PRIORITY_STYLE.get(p, "")

    dep_list = task.get("dependencies", [])
    dep_display = []
    for dep_id in dep_list:
        dep_task = get_task(data, dep_id)
        if dep_task:
            dep_s = dep_task["status"]
            dep_emoji = STATUS_EMOJI.get(dep_s, "")
            dep_display.append(f"{dep_id} {dep_emoji}")
        else:
            dep_display.append(dep_id)

    lines = [
        f"[bold]{task['title']}[/bold]",
        "",
        (f"  [dim]상태[/dim]      [{s_style}]"
         f"{STATUS_EMOJI.get(s, '')} {STATUS_LABEL.get(s, s)}[/{s_style}]"),
        f"  [dim]우선순위[/dim]  [{p_style}]{p}[/{p_style}]",
        f"  [dim]예상 시간[/dim] {task['estimated_minutes']}분",
        f"  [dim]담당자[/dim]    {task.get('assignee') or '-'}",
        f"  [dim]태그[/dim]      {', '.join(task.get('tags', [])) or '-'}",
        f"  [dim]의존[/dim]      {', '.join(dep_display) or '-'}",
        f"  [dim]생성일[/dim]    {task.get('created_at', '-')}",
        f"  [dim]수정일[/dim]    {task.get('updated_at', '-')}",
        f"  [dim]문서[/dim]      [dim]{task.get('doc', '-')}[/dim]",
        "",
        "[bold]설명[/bold]",
        f"  {task.get('description', '-')}",
    ]
    if task.get("notes"):
        lines += ["", "[bold]메모[/bold]", f"  {task['notes']}"]

    console.print(
        Panel(
            "\n".join(lines),
            title=f"[bold cyan]{task['id']}[/bold cyan]",
            border_style="blue",
            padding=(1, 2),
        )
    )


# ── add ───────────────────────────────────────────────────────────────────────


def cmd_add(args) -> None:
    data = load_backlog()
    new_id = next_task_id(data)

    console.print(f"\n[bold]새 태스크 추가[/bold]  ID: [cyan]{new_id}[/cyan]\n")

    title = Prompt.ask("[bold]제목[/bold]")
    description = Prompt.ask("[bold]설명[/bold]")
    priority = Prompt.ask(
        "우선순위", choices=VALID_PRIORITIES, default="medium"
    )
    initial_status = Prompt.ask(
        "초기 상태", choices=VALID_STATUSES, default="todo"
    )
    estimated = Prompt.ask("예상 시간(분)", default="30")
    deps_raw = Prompt.ask(
        "의존 태스크 [dim](쉼표 구분, 없으면 엔터)[/dim]", default=""
    )
    tags_raw = Prompt.ask(
        "태그 [dim](쉼표 구분, 없으면 엔터)[/dim]", default=""
    )
    assignee = Prompt.ask("담당자 [dim](없으면 엔터)[/dim]", default="")
    notes = Prompt.ask("메모 [dim](없으면 엔터)[/dim]", default="")

    dependencies = [d.strip().upper() for d in deps_raw.split(",") if d.strip()]
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    # 의존 태스크 존재 여부 확인
    existing_ids = {t["id"] for t in data["tasks"]}
    invalid_deps = [d for d in dependencies if d not in existing_ids]
    if invalid_deps:
        console.print(
            f"[yellow]⚠ 존재하지 않는 의존 태스크: {', '.join(invalid_deps)}[/yellow]"
        )

    today = datetime.now().strftime("%Y-%m-%d")
    doc_path = f"tasks/{new_id}.md"

    new_task = {
        "id": new_id,
        "title": title,
        "description": description,
        "doc": doc_path,
        "status": initial_status,
        "priority": priority,
        "estimated_minutes": int(estimated),
        "dependencies": dependencies,
        "tags": tags,
        "assignee": assignee or None,
        "created_at": today,
        "updated_at": today,
        "notes": notes,
    }

    # 미리 보기
    console.print()
    console.print(
        Panel(
            f"[bold]{title}[/bold]\n\n{description}",
            title=f"[cyan]{new_id}[/cyan]  미리보기",
            border_style="dim",
        )
    )

    if not Confirm.ask(f"[cyan]{new_id}[/cyan] 태스크를 추가하시겠습니까?"):
        console.print("[dim]취소됐습니다.[/dim]")
        return

    data["tasks"].append(new_task)
    save_backlog(data)

    # 상세 .md 파일 자동 생성
    TASKS_DIR.mkdir(exist_ok=True)
    md_content = f"""# {new_id} · {title}

| 항목 | 내용 |
|------|------|
| 상태 | {initial_status} |
| 우선순위 | {priority} |
| 예상 시간 | {estimated}분 |
| 의존 | {', '.join(dependencies) or '없음'} |

## 목표

{description}

## 완료 조건

- [ ] (완료 조건을 여기에 작성하세요)

## 작업 내용

(작업 내용을 여기에 작성하세요)

## 주의사항

(주의사항을 여기에 작성하세요)
"""
    (TASKS_DIR / f"{new_id}.md").write_text(md_content, encoding="utf-8")

    console.print(f"\n[green]✅ {new_id} 태스크가 추가됐습니다.[/green]")
    console.print(f"   상세 문서: [dim]{doc_path}[/dim]")


# ── update ────────────────────────────────────────────────────────────────────


def cmd_update(args) -> None:
    data = load_backlog()
    task = get_task(data, args.id)
    if not task:
        console.print(f"[red]'{args.id}' 태스크를 찾을 수 없습니다.[/red]")
        sys.exit(1)

    changed = []

    if args.status:
        old = task["status"]
        task["status"] = args.status
        changed.append(
            f"상태: [{STATUS_STYLE[old]}]{STATUS_LABEL[old]}[/{STATUS_STYLE[old]}]"
            f" → [{STATUS_STYLE[args.status]}]{STATUS_LABEL[args.status]}"
            f"[/{STATUS_STYLE[args.status]}]"
        )

    if args.priority:
        old = task["priority"]
        task["priority"] = args.priority
        changed.append(f"우선순위: {old} → {args.priority}")

    if args.title:
        task["title"] = args.title
        changed.append(f"제목: {args.title}")

    if args.description:
        task["description"] = args.description
        changed.append("설명 업데이트")

    if args.assignee is not None:
        task["assignee"] = args.assignee or None
        changed.append(f"담당자: {args.assignee or '-'}")

    if args.notes is not None:
        task["notes"] = args.notes
        changed.append("메모 업데이트")

    if args.deps is not None:
        deps = [d.strip().upper() for d in args.deps.split(",") if d.strip()]
        task["dependencies"] = deps
        changed.append(f"의존: {', '.join(deps) or '-'}")

    if args.tags is not None:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        task["tags"] = tags
        changed.append(f"태그: {', '.join(tags) or '-'}")

    if args.estimated:
        task["estimated_minutes"] = int(args.estimated)
        changed.append(f"예상 시간: {args.estimated}분")

    if not changed:
        console.print(
            "[yellow]변경할 항목이 없습니다. --help 로 옵션을 확인하세요.[/yellow]"
        )
        return

    task["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    save_backlog(data)

    console.print(f"\n[green]✅ {task['id']} 업데이트 완료[/green]")
    for c in changed:
        console.print(f"   • {c}")
    console.print()


# ── open ──────────────────────────────────────────────────────────────────────


def cmd_open(args) -> None:
    data = load_backlog()
    task = get_task(data, args.id)
    if not task:
        console.print(f"[red]'{args.id}' 태스크를 찾을 수 없습니다.[/red]")
        sys.exit(1)

    doc_path = BACKLOG_PATH.parent / task.get("doc", "")
    if not doc_path.exists():
        console.print(f"[red]상세 문서를 찾을 수 없습니다: {doc_path}[/red]")
        sys.exit(1)

    console.print(f"[dim]열기: {doc_path}[/dim]")
    system = platform.system()
    if system == "Windows":
        os.startfile(str(doc_path))
    elif system == "Darwin":
        subprocess.run(["open", str(doc_path)])
    else:
        subprocess.run(["xdg-open", str(doc_path)])


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="backlog",
        description="WIP 재공 현황판 Backlog CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python backlog_cli.py list
  python backlog_cli.py list --status todo
  python backlog_cli.py list --status waiting --priority high
  python backlog_cli.py list --tag setup
  python backlog_cli.py show TASK-001
  python backlog_cli.py add
  python backlog_cli.py update TASK-001 --status in_progress
  python backlog_cli.py update TASK-001 --assignee 홍길동 --notes "진행 중"
  python backlog_cli.py update TASK-001 --deps "TASK-003,TASK-005"
  python backlog_cli.py open TASK-001
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="태스크 목록 조회")
    p_list.add_argument(
        "--status", choices=VALID_STATUSES, metavar="STATUS",
        help=f"상태 필터 ({', '.join(VALID_STATUSES)})",
    )
    p_list.add_argument(
        "--priority", choices=VALID_PRIORITIES, metavar="PRIORITY",
        help="우선순위 필터 (high, medium, low)",
    )
    p_list.add_argument("--tag", metavar="TAG", help="태그 필터")

    # show
    p_show = subparsers.add_parser("show", help="태스크 상세 조회")
    p_show.add_argument("id", help="태스크 ID (예: TASK-001)")

    # add
    subparsers.add_parser("add", help="새 태스크 추가 (대화형)")

    # update
    p_update = subparsers.add_parser("update", help="태스크 필드 수정")
    p_update.add_argument("id", help="태스크 ID")
    p_update.add_argument("--status", choices=VALID_STATUSES, metavar="STATUS", help="상태 변경")
    p_update.add_argument("--priority", choices=VALID_PRIORITIES,
                          metavar="PRIORITY", help="우선순위 변경")
    p_update.add_argument("--title", metavar="TITLE", help="제목 변경")
    p_update.add_argument("--description", metavar="DESC", help="설명 변경")
    p_update.add_argument("--assignee", metavar="NAME",
                          help='담당자 변경 (비우려면 빈 문자열 "")')
    p_update.add_argument("--notes", metavar="TEXT", help="메모 변경")
    p_update.add_argument("--deps", metavar="IDs",
                          help="의존 태스크 변경 (쉼표 구분, 예: TASK-001,TASK-002)")
    p_update.add_argument("--tags", metavar="TAGS", help="태그 변경 (쉼표 구분)")
    p_update.add_argument("--estimated", metavar="MINUTES", help="예상 시간(분) 변경")

    # open
    p_open = subparsers.add_parser("open", help="상세 문서(.md) 열기")
    p_open.add_argument("id", help="태스크 ID")

    args = parser.parse_args()

    {
        "list": cmd_list,
        "show": cmd_show,
        "add": cmd_add,
        "update": cmd_update,
        "open": cmd_open,
    }[args.command](args)


if __name__ == "__main__":
    main()
