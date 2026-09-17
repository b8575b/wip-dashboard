# TASK-008 · WIP Matrix 화면 표시

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-007 |

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
