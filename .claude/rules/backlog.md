# Backlog 관리 규칙

## backlog.json 직접 접근 금지

Read / Edit / Write 도구로 `backlog.json`에 접근하지 않는다.
`block_backlog_read.py` hook이 Read 시도를 자동 차단한다.
조회는 CLI 또는 `backlog_dashboard.html` 사용.

```bash
python backlog_cli.py list
python backlog_cli.py show TASK-NNN
```

## 변경 주체

| 행위 | 주체 |
|------|------|
| 상태·담당자·메모 수정 | Claude Code (via CLI) |
| 새 태스크 추가 | Claude Code (via `backlog_cli.py add`) |
| 완료 조건(done_when) 내용 결정 | **사용자** |
| 우선순위 재조정 | **사용자** (Claude는 제안만) |
| 병렬 실행 중 JSON 갱신 | **메인 에이전트만** — 서브에이전트는 갱신 불가 |

## 상태 전이

```
todo → in_progress → review → done
         ↓                        ↑
      waiting                cancelled
         ↓
  pending_decision
```

| 상태 | 의미 | 전환 조건 |
|------|------|----------|
| `todo` | 착수 대기 | deps가 done이 되면 자동 진행 가능 |
| `in_progress` | 작업 중 | deps 전체 done일 때만 전환 가능 |
| `review` | 리뷰 요청 | 구현 완료, subagent 검토 전 |
| `pending_decision` | 사람 판단 필요 | 질문을 남기고 대기 (needs_info 역할) |
| `waiting` | 차단됨 | 미해소 deps 존재 |
| `done` | 완료 | done_when + hook + review 모두 충족 |
| `cancelled` | 취소 | 범위 제외 결정 |

## 결정 필요 시 처리

사람의 결정이 필요한 경우:
1. `--status pending_decision`으로 변경
2. `tasks/TASK-NNN.md` 또는 응답에 질문 명시
3. 답변 수신 전까지 해당 태스크를 진행하지 않는다

리뷰 미실행 · 검사 실패 · 미설정 검사는 `done` 전환 근거가 될 수 없다.

## 착수 전 확인 사항

```bash
python backlog_cli.py show TASK-NNN  # done_when, gate, deps 확인
```

- `dependencies`: 전부 `done`이어야 착수 가능
- `gate`: 화면 표시만 — 코드나 명령으로 실행하지 않는다
- `done_when`: 구현 전 달성 범위 확정

## 병렬 실행 규칙

step 5에서 task-explainer + adversarial-reviewer를 동시에 실행할 때:

- 기준 파일(구현 완료 시점의 `.py` 파일)을 변경하지 않는다
- `backlog.json` 갱신은 병렬 실행이 끝난 뒤 메인 에이전트만 수행
- 두 에이전트의 출력이 모두 수신된 뒤 결과를 통합한다

## 새 태스크 추가

```bash
python backlog_cli.py add   # 대화형 입력
```

- 예상 시간 30분 단위
- `tasks/TASK-NNN.md` 자동 생성
- 태그: setup, supabase, streamlit, ui, data, deployment 등

## 적용 방식

| 규칙 | 지침 | Hook |
|------|:----:|:----:|
| backlog.json 직접 접근 금지 | | ✓ block_backlog_read |
| 변경 주체 제한 (메인만 갱신) | ✓ | |
| deps 미해소 시 착수 금지 | ✓ | |
| gate 코드 실행 금지 | ✓ | |
| pending_decision 시 질문 남기기 | ✓ | |
| 완료 기준 충족 전 done 금지 | ✓ | |
| 상태 전환 즉시 업데이트 | ✓ | (post_write 자동 commit) |
