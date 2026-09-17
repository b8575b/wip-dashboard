# TASK-013 · Product / STEP 필터 구현

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | medium |
| 예상 시간 | 30분 |
| 의존 | TASK-008 |

## 목표

사이드바에 Product 다중 선택, STEP 다중 선택 필터를 추가하고, 필터 변경 시 WIP Matrix에 동일한 조건이 적용되도록 한다.

## 완료 조건

- [ ] 사이드바에 Product 다중 선택 `multiselect` 추가
- [ ] 사이드바에 STEP 다중 선택 `multiselect` 추가
- [ ] 필터 변경 시 WIP Matrix가 필터 조건에 맞게 갱신됨
- [ ] 필터를 모두 해제하면 전체 데이터 기준 Matrix 표시

## 작업 내용

```python
# app.py 사이드바 섹션
with st.sidebar:
    st.header("필터")
    all_products = sorted(df["product_name"].unique().tolist())
    all_steps = sorted(df["step_name"].unique().tolist(), key=lambda s: df[df["step_name"]==s]["step_order"].iloc[0])

    selected_products = st.multiselect("Product", all_products, default=all_products)
    selected_steps = st.multiselect("STEP", all_steps, default=all_steps)

# 필터 적용
filtered_df = df[
    df["product_name"].isin(selected_products) &
    df["step_name"].isin(selected_steps)
]
matrix = build_wip_matrix(filtered_df)
```

## 주의사항

- 필터 기능은 핵심 기능(Matrix + 팝업)보다 우선순위가 낮다. 핵심 흐름이 완전히 동작한 이후에 추가한다
- TASK-014의 Status/Hold 필터와 동일한 `filtered_df`를 공유해야 한다
