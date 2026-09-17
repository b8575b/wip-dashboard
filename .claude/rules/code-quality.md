# 코드 품질 규칙

## 파일별 최대 줄수

실제 적용 기준: `hooks/post_write.py` + `hooks/stop_check.py`의 `MAX_LINES` 딕셔너리.

| 파일 | 최대 줄수 | 경고(85%) |
|------|-----------|-----------|
| `app.py` | 300줄 | 255줄 |
| `backlog_cli.py` | 550줄 | 468줄 |
| `db.py` | 100줄 | 85줄 |
| `hooks/*.py` | 100줄 | 85줄 |
| 그 외 `*.py` | 150줄 | 128줄 |

한계 초과 시 hook이 block을 반환한다. 파일을 분리하거나 함수를 추출한다.

## 코드 책임 분리

각 파일은 단일 책임을 갖는다. 교차 배치 금지.

| 파일 | 책임 | 한계 |
|------|------|------|
| `app.py` | Streamlit 진입점, UI 조합 | 300줄 |
| `db.py` | Supabase 클라이언트 초기화 전용 | 100줄 |
| `data/fetch.py` | WIP 데이터 Supabase 조회 | 150줄 |
| `data/aggregate.py` | Pandas pivot 집계 | 150줄 |
| `ui/matrix.py` | Matrix 표시 컴포넌트 (분리 필요 시) | 150줄 |
| `ui/lot_dialog.py` | Lot 팝업 컴포넌트 (분리 필요 시) | 150줄 |
| `hooks/*.py` | 각 hook 단일 역할 | 100줄 |
| `backlog_cli.py` | Backlog CLI 전용 | 550줄 |

`app.py`가 255줄을 넘으면 해당 UI를 `ui/` 하위 모듈로 분리한다.

## 자동 검사 (PostToolUse hook)

`hooks/post_write.py`가 `.py` 파일 Write/Edit 마다 자동 실행:

1. 줄수 검사 (85% 경고 / 100% block)
2. `py_compile` 구문 검사 (E999)
3. `flake8 --max-line-length=100 --extend-ignore=W503,E303`

`hooks/stop_check.py`가 세션 Stop 이벤트 시 전체 `.py` 파일을 재검사.

hook이 block을 반환하면 반드시 수정 후 재작업. 오류를 무시하거나 우회하지 않는다.

## 줄 길이

줄당 최대 100자. 초과 시 암묵적 줄 이음으로 나눈다.

```python
result = (
    some_long_function(arg1, arg2)
    + another_function(arg3)
)
```

## 주석 최소화

WHY가 비명백한 경우에만 한 줄 주석. docstring 작성 금지.
`st.` API 호출에 설명 주석 붙이지 않는다.

## 적용 방식

| 규칙 | 지침 | Hook |
|------|:----:|:----:|
| 파일별 줄수 한계 | | ✓ post_write / stop_check |
| 구문 오류 금지 | | ✓ post_write |
| lint 위반 금지 | | ✓ post_write / stop_check |
| 코드 책임 분리 | ✓ | (줄수 초과 시 간접 강제) |
| 줄 길이 100자 | | ✓ flake8 E501 |
| 주석 최소화 | ✓ | |
