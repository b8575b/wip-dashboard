# 워크플로우·문서 갱신 규칙

## 문서 갱신 시점

| 문서 | 갱신 시점 | 담당 |
|------|----------|------|
| `tasks/TASK-NNN.md` | step 5 병렬 실행 중 | task-explainer (자동) |
| `backlog.json` | 각 상태 전환 즉시 | Claude Code via CLI |
| `CLAUDE.md` | 프로젝트 구조·규칙 변경 시 | 사용자 또는 Claude |
| `.claude/rules/*.md` | 규칙 변경 시 | 사용자 또는 Claude |
| `backlog_dashboard.html` | 기능 요건 변경 시 | Claude Code |

`tasks/TASK-NNN.md` 갱신 시점:
- `in_progress` 전환 직전: task-explainer가 "쉬운 설명 + 관련 파일" 섹션 추가
- step 5: 구현 완료 후 task-explainer가 문서 보완

## Rules 로딩 경로

Claude Code는 세션 시작 시 다음 파일들을 **project instructions**로 자동 로딩한다.
별도 import·require 불필요.

```
로딩 순서:
1. CLAUDE.md                     (프로젝트 루트)
2. .claude/rules/*.md             (알파벳 순, 전체 로딩)
3. .claude/agents/*.md            (호출 시에만 로딩)
4. .claude/settings.json          (hook 등록)
```

**로딩 검증**: 이 세션의 system-reminder에 모든 rules 파일 내용이 포함됨으로써
확인. 추가 설정 없이 `.claude/rules/` 내 `.md` 파일은 자동 반영된다.

현재 로딩 중인 rules 파일:
- `backlog.md` — 변경 주체, 상태 전이, 병렬 실행
- `code-quality.md` — 줄수 한계, 코드 책임
- `git.md` — 브랜치, commit, secrets
- `streamlit.md` — st.secrets, 캐싱, UI 패턴
- `subagents.md` — 호출 시점, 병렬 실행, 피드백
- `workflow.md` — 이 파일 (문서 갱신, 로딩 검증, 전체 적용 표)

## 완료 차단 조건

아래 중 하나라도 해당하면 `done`으로 전환하지 않는다:

| 조건 | 설명 |
|------|------|
| `done_when` 미달성 | 완료 조건 항목 중 미충족 항목 존재 |
| hook block 미해소 | post_write 또는 stop_check가 block 반환 |
| adversarial-reviewer 미실행 | `.py` 변경 후 리뷰를 실행하지 않은 경우 |
| 심각도 높음 미수정 | adversarial-reviewer 결과 중 높음 항목 잔존 |
| 미설정 검사 통과 처리 | NOT_CONFIGURED 상태를 완료 근거로 사용 |

## 전체 규칙 적용 방식

| 규칙 | 지침 | Hook | 리뷰 |
|------|:----:|:----:|:----:|
| **Backlog** | | | |
| backlog.json 직접 접근 금지 | | ✓ block_backlog_read | |
| 메인 에이전트만 JSON 갱신 | ✓ | | |
| deps 미해소 시 착수 금지 | ✓ | | |
| gate 코드 실행 금지 | ✓ | | |
| pending_decision 시 질문 명시 | ✓ | | |
| 상태 즉시 업데이트 | ✓ | (post_write 자동 commit) | |
| **코드 품질** | | | |
| 파일별 줄수 한계 | | ✓ post_write / stop_check | |
| 구문 오류 금지 | | ✓ post_write (py_compile) | |
| lint 위반 금지 | | ✓ post_write / stop_check | |
| Supabase 키 하드코딩 금지 | | ✓ secrets_guard | |
| 코드 책임 분리 | ✓ | (줄수 초과 간접 강제) | |
| **Git** | | | |
| main 브랜치 개발 금지 | ✓ | (session_start 안내) | |
| secrets.toml commit 금지 | | ✓ git_safety | |
| **Streamlit** | | | |
| st.secrets 사용 | | ✓ secrets_guard | ✓ adversarial |
| st.cache_resource/data 적용 | ✓ | | ✓ adversarial |
| **Subagents** | | | |
| task-explainer 실행 (문서화) | ✓ | | ✓ task-explainer |
| adversarial-reviewer 실행 | ✓ | | ✓ adversarial |
| 심각도 높음 미수정 시 done 금지 | ✓ | | ✓ adversarial |
| 병렬 실행 중 기준 파일 변경 금지 | ✓ | | |
| 리뷰 미실행은 완료 근거 불가 | ✓ | | |
| **완료 조건** | | | |
| done_when 미달성 시 done 금지 | ✓ | | ✓ adversarial |
| hook block 미해소 시 done 금지 | | ✓ | |
| 미설정 검사 통과 처리 금지 | ✓ | | |
