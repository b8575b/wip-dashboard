# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

품질 담당자가 제품별·공정 STEP별 재공(WIP) 수량을 Matrix 형태로 확인하고,
수량 선택 시 해당 Lot 상세정보를 팝업으로 조회하는 **웹 기반 재공 현황판**.

- **대상 사용자**: 품질 담당자
- **핵심 흐름**: WIP Matrix → Product/STEP 선택 → Lot 상세 팝업
- **데모용 가상 데이터** 사용 (실제 제조 시스템 연동 제외)

## Tech Stack

| 역할 | 기술 |
|------|------|
| Language | Python 3.10 |
| UI | Streamlit ≥ 1.35 (단일 앱) |
| Data | Pandas |
| Visualization | Plotly |
| Database | Supabase PostgreSQL |
| Deployment | Streamlit Community Cloud + GitHub |

React / Next.js / Vue 등 별도 프론트엔드는 사용하지 않는다.

## Commands

```bash
# 앱 실행
pip install -r requirements.txt
streamlit run app.py

# Backlog 조회 (CLI 전용 — backlog.json 직접 접근 금지)
python backlog_cli.py list                           # 전체 목록
python backlog_cli.py list --status todo             # 상태 필터
python backlog_cli.py show TASK-NNN                  # 상세 조회
python backlog_cli.py update TASK-NNN --status done  # 상태 변경
python backlog_cli.py add                            # 새 태스크 추가

# 대시보드 (브라우저에서 열기)
start backlog_dashboard.html   # Windows
open  backlog_dashboard.html   # macOS
```

상세 규칙은 `.claude/rules/backlog.md` 참고.

## Project Structure

```
lecture_practice/
├── app.py                    # Streamlit 진입점 (TASK-002)
├── db.py                     # Supabase 클라이언트 초기화
├── data/
│   ├── fetch.py              # WIP 데이터 조회
│   └── aggregate.py          # Pandas pivot 집계
├── sources/rawdata.csv       # WIP 원본 데이터
├── scripts/load_data.py      # CSV → Supabase 초기 적재 (1회성)
├── tasks/TASK-NNN.md         # 태스크별 작업 문서
├── hooks/
│   ├── block_backlog_read.py # PreToolUse: backlog.json Read 차단
│   ├── git_safety.py         # PreToolUse: git add 보안 검사
│   ├── post_write.py         # PostToolUse: 줄수·구문·lint + backlog commit
│   ├── secrets_guard.py      # PostToolUse: Supabase 키 하드코딩 차단
│   ├── stop_check.py         # Stop: 전체 .py 줄수·lint 최종 검사
│   └── session_start.py      # SessionStart: 브랜치 확인
├── .claude/
│   ├── settings.json         # Hook 설정
│   ├── agents/
│   │   ├── task-explainer.md        # Haiku: 태스크 설명 + 파일 탐색
│   │   └── adversarial-reviewer.md  # Opus: 적대적 코드 리뷰
│   └── rules/                # 프로젝트 규칙 (자동 로딩)
├── .streamlit/secrets.toml   # 로컬 전용 Secrets (git 제외)
├── backlog.json              # 태스크 목록 (CLI로만 조작)
├── backlog_cli.py            # Backlog 관리 CLI
├── backlog_dashboard.html    # Backlog 조회 대시보드
└── requirements.txt
```

## Environment / Secrets

Supabase 접속 정보는 코드에 절대 작성하지 않는다.

```toml
# .streamlit/secrets.toml  ← 로컬 전용, git 커밋 금지
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

Streamlit Community Cloud 배포 시 서비스 내 Secrets 관리 기능으로 주입한다.

## Data Model

`sources/rawdata.csv` → Supabase `wip_inventory` 테이블

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `id` | bigint PK | 레코드 ID |
| `product_name` | text | 제품명 (PRODUCT_A …) |
| `step_order` | integer | STEP 순서 (10, 20, 30 …) |
| `step_name` | text | STEP 명칭 (STEP_010 …) |
| `lot_id` | text | Lot 식별자 |
| `quantity` | integer | 수량 |
| `equipment` | text | 설비 ID |
| `input_time` | timestamp | 투입 시간 |
| `waiting_hours` | numeric | 대기 시간(h) |
| `status` | text | RUN / WAIT / HOLD |
| `hold_yn` | text | Y / N |
| `created_at` | timestamp | 스냅샷 기록 시각 |

WIP Matrix 셀 값 = `product_name + step_name` 기준 `quantity` SUM

## Core User Flow

1. 앱 접속 → Product × STEP WIP Matrix 표시
2. 특정 셀(Product + STEP) 선택
3. 해당 조건의 Lot 상세정보를 `st.dialog`로 팝업 표시

Matrix 셀 직접 클릭이 불안정하면 selectbox 조합 대체 가능. **3단계 흐름은 반드시 유지.** → TASK-009

## Scope Boundaries

**Must Have**: Supabase 연결, WIP 조회, Matrix 표시, Lot 상세 팝업, 배포

**Should Have**: Product / STEP / Status / Hold 필터

**구현 제외**: 데이터 생성·수정, 사용자 인증, 알림, 예측, 실시간 스트리밍, LLM 연동

---

## 작업 실행 순서

세션이 중단되어도 `python backlog_cli.py list` 로 재개 위치를 확인한다.

### 1. 기준 문서와 백로그 확인

- 요구사항: `CLAUDE.md`, `.claude/rules/` (자동 로딩됨)
- 현황: `python backlog_cli.py list`
- 상세: `python backlog_cli.py show TASK-NNN`
- `backlog.json` 직접 읽기 금지 — CLI 또는 `backlog_dashboard.html` 사용

### 2. 수행 가능한 태스크 선택

- `dependencies`가 모두 `done`인 태스크만 착수
- `gate` 조건은 화면 표시만 — 코드나 명령으로 실행하지 않는다
- `done_when` 항목을 읽고 구현 전 범위를 확정한다
- 사람의 결정이 필요하면 `pending_decision`으로 변경 후 질문을 남긴다

### 3. 착수 기록

```bash
python backlog_cli.py update TASK-NNN --status in_progress
python backlog_cli.py update TASK-NNN --assignee 이름 --estimated 30
```

실제 착수 시각에 맞게 기록한다. hook이 backlog.json 변경을 자동 commit한다.

### 4. 구현 + 자동 훅 검사

- `.claude/rules/code-quality.md` 파일별 줄수 한계 준수
- `.py` 저장마다 `post_write.py` hook 자동 실행: 줄수 → py_compile → flake8
- hook `block` → 반드시 수정 후 재작업. 우회 금지

### 5. 기준 입력 고정 후 서브에이전트 병렬 실행

구현이 완료된 시점의 파일을 기준으로 두 에이전트를 **동시에** 실행한다.
병렬 실행 중에는 기준 파일을 변경하지 않는다.
`backlog.json` 갱신은 메인 에이전트만 담당한다.

```
[task-explainer  · Haiku]           [adversarial-reviewer · Opus]
tasks/TASK-NNN.md에                 변경된 .py 파일의 버그·
쉬운 설명·관련 파일 추가             설계·보안·성능 이슈 분석
```

상세 호출 방법: `.claude/rules/subagents.md`

### 6. 결과 통합 및 수정

- 심각도 높음 → 반드시 수정
- 심각도 중간 → 사용자 확인 후 결정
- 수정 후 `stop_check.py`가 클린 패스하는지 재검증

### 7. 완료 기록

아래 조건이 **모두** 충족될 때만 `done`으로 변경한다.
리뷰 미실행 · 검사 실패 · 미설정 검사는 완료 근거가 될 수 없다.

- `done_when` 항목 전체 달성
- hook 검사 클린 패스 (block 없음)
- adversarial-reviewer 심각도 높음 0건

```bash
python backlog_cli.py update TASK-NNN --status done
```

→ hook이 자동으로 `git add -A && git commit && git push` 실행

### 8. 문서·대시보드 최신 상태 확인

- `backlog_dashboard.html` 브라우저에서 열고 JSON 재선택
- `tasks/TASK-NNN.md` 갱신 반영 여부 확인

### 9. 상태 즉시 기록 원칙

각 전환 시점에 **즉시** backlog.json을 업데이트한다. 일괄 처리 금지.

| 전환 상황 | CLI 명령 |
|----------|----------|
| 착수 | `--status in_progress` |
| 차단 (의존 미해소) | `--status waiting` |
| 결정 필요 (사람 판단) | `--status pending_decision` |
| 리뷰 요청 | `--status review` |
| 완료 | `--status done` |

---

## Automated Hooks

`.claude/settings.json` 기준. 실제 파일: `hooks/` 디렉터리.

| Hook 파일 | 이벤트 | 트리거 조건 | 동작 |
|-----------|--------|-------------|------|
| `block_backlog_read` | PreToolUse | Read on `backlog.json` | 차단 + CLI 안내 |
| `git_safety` | PreToolUse | Bash — `git add` 포함 | secrets.toml 명시 → 차단 / gitignore 미등록 → 경고 |
| `post_write` | PostToolUse | Write\|Edit on `*.py` | 줄수·py_compile·flake8 검사 |
| `post_write` | PostToolUse | Write\|Edit on `backlog.json` | 자동 git commit (done 감지 시 push) |
| `secrets_guard` | PostToolUse | Write\|Edit on `*.py` | Supabase URL·Key 하드코딩 → 차단 |
| `stop_check` | Stop | 세션 종료 | 전체 `.py` 줄수·lint 최종 검사 |
| `session_start` | SessionStart | 세션 시작 | 브랜치 표시, main이면 dev 전환 안내 |

## Code Length Limits

실제 적용 기준 (`hooks/post_write.py`, `hooks/stop_check.py`의 `MAX_LINES`):

| 파일 | 최대 줄수 | 경고(85%) |
|------|-----------|-----------|
| `app.py` | 300줄 | 255줄 |
| `backlog_cli.py` | 550줄 | 468줄 |
| `db.py` | 100줄 | 85줄 |
| `hooks/*.py` | 100줄 | 85줄 |
| 그 외 `*.py` | 150줄 | 128줄 |

## Rules 적용 방식 요약

각 규칙의 강제 수단. 세부 내용은 `.claude/rules/` 참고.

| 규칙 | 지침 | Hook | 리뷰 |
|------|:----:|:----:|:----:|
| backlog.json 직접 접근 금지 | | ✓ block_backlog_read | |
| secrets.toml git add 금지 | | ✓ git_safety | |
| .py 줄수 한계 | | ✓ post_write / stop_check | |
| .py 구문 오류 금지 | | ✓ post_write | |
| .py lint 위반 금지 | | ✓ post_write / stop_check | |
| Supabase 키 하드코딩 금지 | | ✓ secrets_guard | |
| deps 미해소 시 착수 금지 | ✓ | | |
| main 브랜치 직접 개발 금지 | ✓ | (session_start 안내) | |
| 병렬 실행 중 기준 파일 변경 금지 | ✓ | | |
| gate 코드 실행 금지 | ✓ | | |
| st.secrets 사용 (URL·Key 직접 기재 금지) | | ✓ secrets_guard | ✓ adversarial |
| 심각도 높음 미수정 시 done 금지 | ✓ | | ✓ adversarial |
| done_when 미달성 시 done 금지 | ✓ | | ✓ adversarial |
| 리뷰 미실행은 완료 근거 불가 | ✓ | | |
| 상태 전환 즉시 backlog 업데이트 | ✓ | (post_write 자동 commit) | |
| tasks/TASK-NNN.md 착수 전 갱신 | | | ✓ task-explainer |
| tasks/TASK-NNN.md 완료 전 갱신 | | | ✓ task-explainer |

## Rules 파일 위치

`.claude/rules/` 디렉터리의 `.md` 파일은 Claude Code가 세션 시작 시 자동으로
project instructions로 로딩한다. 별도 설정 불필요.

| 파일 | 다루는 내용 |
|------|------------|
| `backlog.md` | 변경 주체, 상태 전이, 병렬 실행 규칙, 결정 처리 |
| `code-quality.md` | 파일별 줄수, 코드 책임 분리, lint 기준 |
| `git.md` | 브랜치 전략, 자동 commit, secrets 보호 |
| `streamlit.md` | st.secrets, 캐싱, session_state, dialog |
| `subagents.md` | 호출 시점, 병렬 실행, 피드백 처리, 완료 차단 조건 |
| `workflow.md` | 문서 갱신 시점, 적용 경로, rules 로딩 검증 |
