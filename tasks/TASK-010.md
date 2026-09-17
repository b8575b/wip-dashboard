# TASK-010 · Product + STEP 선택 처리 구현

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-009 |

## 목표

TASK-009에서 결정된 방식으로 사용자가 특정 Product와 STEP을 선택하는 UI를 구현한다. 선택값을 `st.session_state`에 저장하여 이후 Lot 조회에 전달한다.

## 완료 조건

- [ ] 사용자가 Product + STEP을 선택할 수 있는 UI 구현
- [ ] 선택값이 `st.session_state["selected_product"]`, `st.session_state["selected_step"]`에 저장됨
- [ ] 선택값 변경 시 화면이 올바르게 갱신됨
- [ ] 아직 선택 전인 상태에서 팝업이 열리지 않음

## 작업 내용 (옵션 A 기준)

```python
event = st.dataframe(
    matrix.style.applymap(lambda v: "color: #cccccc;" if v == 0 else ""),
    on_select="rerun",
    selection_mode="single-cell",
    use_container_width=True
)

if event.selection.rows and event.selection.columns:
    st.session_state["selected_product"] = matrix.index[event.selection.rows[0]]
    st.session_state["selected_step"] = matrix.columns[event.selection.columns[0]]
```

## 작업 내용 (옵션 B 기준)

```python
col1, col2, col3 = st.columns([2, 2, 1])
product = col1.selectbox("Product", matrix.index.tolist(), key="selected_product")
step = col2.selectbox("STEP", matrix.columns.tolist(), key="selected_step")
show_detail = col3.button("상세 조회", use_container_width=True)
```

## 주의사항

- session_state 키를 일관되게 유지해야 TASK-011의 Lot 조회 함수와 연동됨
- Matrix에서 수량이 0인 셀이 선택됐을 때도 팝업이 열리되, "해당 조건의 재공이 없습니다" 안내를 표시한다
