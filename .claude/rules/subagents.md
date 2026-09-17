# 서브에이전트 사용 규칙

에이전트 정의: `.claude/agents/task-explainer.md` (Haiku),
`.claude/agents/adversarial-reviewer.md` (Opus).

## 실행 순서 (작업 step 5)

구현 완료 후, 기준 파일 버전을 고정한 상태에서 두 에이전트를 **병렬** 실행한다.

```
구현 완료 (step 4)
        ↓
  [기준 파일 고정]   ← 이후 변경 금지 (병렬 실행 중)
        ↓
task-explainer  ┐  동시 실행
adversarial     ┘
        ↓
  두 결과 수신 후 통합 (step 6)
        ↓
  심각도 높음 수정 → 재검증 → done (step 7)
```

## task-explainer (Haiku) — 문서화

**역할**: `tasks/TASK-NNN.md`에 쉬운 설명 + 관련 파일 목록 기록.

**호출 시점**: 병렬 실행 단계(step 5). 이전 호출로 "쉬운 설명" 섹션이 이미 있으면 건너뛴다.

**호출 방법**:
```
task-explainer에게 TASK-NNN을 분석해달라고 요청
```

**작업 내용**:
1. `python backlog_cli.py show TASK-NNN` 으로 태스크 정보 조회
2. 비기술적 언어로 2–3문장 설명 작성
3. Glob + Grep으로 관련 파일 탐색
4. `tasks/TASK-NNN.md` 상단에 "쉬운 설명" + "관련 파일" 섹션 추가

**건너뛸 수 있는 경우**:
- `tasks/TASK-NNN.md`에 "쉬운 설명" 섹션이 이미 존재할 때

## adversarial-reviewer (Opus) — 비판적 검토

**역할**: 변경된 `.py` 파일의 결함·설계·보안·성능 이슈를 적대적 시각으로 분석.

**호출 시점**: 병렬 실행 단계(step 5). `.py` 파일 변경이 없으면 호출하지 않는다.

**호출 방법**:
```
adversarial-reviewer에게 [파일 목록]과 TASK-NNN에 대한 적대적 리뷰를 요청
```

**호출 불필요한 경우**:
- `tasks/*.md`, `backlog.json`, `.md` 파일만 변경했을 때
- `sources/rawdata.csv` 등 데이터 파일만 변경했을 때

## 피드백 처리

| 심각도 | 처리 |
|--------|------|
| 높음 | **반드시 수정** — 미수정 시 `done` 전환 불가 |
| 중간 | 사용자에게 확인 후 결정 |
| 낮음 | 현재 태스크 범위 내에서 판단 |

심각도 높음이 남아 있으면 step 7 `done` 기록을 진행하지 않는다.
adversarial-reviewer 미실행은 완료 근거가 될 수 없다.

## 병렬 실행 규칙

- 병렬 실행 시작 전에 기준 입력(구현 완료 파일)을 고정한다
- 실행 중 기준 파일을 변경하지 않는다
- `backlog.json` 갱신은 병렬 실행이 끝난 뒤 메인 에이전트만 수행한다
- 두 에이전트의 결과가 모두 수신된 후 통합한다

## 적용 방식

| 규칙 | 지침 | 리뷰 |
|------|:----:|:----:|
| task-explainer 실행 (문서화) | ✓ | ✓ task-explainer |
| adversarial-reviewer 실행 | ✓ | ✓ adversarial |
| 심각도 높음 미수정 시 done 금지 | ✓ | ✓ adversarial |
| 병렬 실행 중 기준 파일 변경 금지 | ✓ | |
| 리뷰 미실행은 완료 근거 불가 | ✓ | |
| st.secrets 사용 확인 | | ✓ adversarial |
| 보안·성능 이슈 확인 | | ✓ adversarial |
