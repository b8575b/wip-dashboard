# TASK-008 · WIP Matrix 화면 표시

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-007 |

## 쉬운 설명

TASK-007에서 만든 제품별·STEP별 재공량 표(pivot table)를 웹 화면에 보기 좋게 표시하는 단계입니다. 행은 제품명, 열은 STEP 이름, 셀에는 수량이 들어간 표 형태로 대시보드에 띄우게 됩니다. 수량이 없는 셀(0)은 회색으로 표시해서 한눈에 구분하고, 데이터가 없을 때는 사용자에게 안내 메시지를 보여줍니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `app.py` | 기존 파일 | Streamlit 진입점 — 여기에 Matrix 표시 로직 추가 |
| `data/fetch.py` | 기존 파일 | WIP 원본 데이터 조회 — 이 함수의 반환값을 표시 |
| `data/aggregate.py` | 기존 파일 | `build_wip_matrix(df)` 함수 — TASK-007에서 구현한 pivot 함수 |

## 목표

`build_wip_matrix()`가 반환한 pivot table을 Streamlit 화면에 행=Product, 열=STEP, 셀=WIP 수량 형태로 표시한다.

## 완료 조건

- [ ] WIP Matrix가 화면에 올바르게 렌더링됨
- [ ] 수량 0인 셀과 수량이 있는 셀이 시각적으로 구분됨
- [ ] 데이터가 없을 때 적절한 안내 메시지 표시

## 작업 내용

```python
# app.py 내 Matrix 표시 섹션
from data.fetch import fetch_wip_data
from data.aggregate import build_wip_matrix

df = fetch_wip_data()
matrix = build_wip_matrix(df)

st.subheader("WIP Matrix")

if matrix.empty:
    st.warning("표시할 WIP 데이터가 없습니다.")
else:
    # 수량 0 셀 회색 처리
    styled = matrix.style.applymap(
        lambda v: "color: #cccccc;" if v == 0 else "font-weight: bold;"
    )
    st.dataframe(styled, use_container_width=True)
```

## 선택 옵션

- `st.dataframe`: 정렬, 스크롤 지원 — TASK-009에서 `on_select` 이벤트 활용 가능
- `st.table`: 정적 테이블 — 선택 이벤트 없음

TASK-009 결정 이전에는 `st.dataframe`을 기본으로 사용한다.

## 주의사항

- `use_container_width=True`로 화면 너비에 맞게 확장
- 열이 많아질 경우 가로 스크롤이 발생할 수 있음
