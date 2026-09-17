# TASK-009 · Matrix 셀 선택 UX 방식 결정

| 항목 | 내용 |
|------|------|
| 상태 | pending_decision |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-008 |

## 목표

Streamlit 기술 제약 내에서 사용자가 Matrix에서 특정 Product + STEP을 선택하는 UX 방식을 확정한다.

## 결정이 필요한 이유

Streamlit에서 DataFrame 셀 직접 클릭은 버전 및 구현 방식에 따라 동작이 불안정할 수 있다. 두 방식의 장단점을 검토하여 최종 방향을 선택해야 한다.

## 옵션 비교

| 항목 | 옵션 A: st.dataframe on_select | 옵션 B: selectbox 조합 |
|------|-------------------------------|----------------------|
| UX | Matrix 셀 클릭 → 팝업 | 드롭다운 선택 → 팝업 |
| 안정성 | Streamlit 1.35+ 필요, 실험적 | 모든 버전에서 안정적 |
| 구현 난이도 | 중간 | 낮음 |
| 사용자 흐름 | 직관적 | 2단계 조작 필요 |

### 옵션 A 구현 스케치

```python
event = st.dataframe(matrix, on_select="rerun", selection_mode="single-cell")
if event.selection.rows and event.selection.columns:
    product = matrix.index[event.selection.rows[0]]
    step = matrix.columns[event.selection.columns[0]]
```

### 옵션 B 구현 스케치

```python
col1, col2 = st.columns(2)
product = col1.selectbox("Product", matrix.index.tolist())
step = col2.selectbox("STEP", matrix.columns.tolist())
if st.button("상세 조회"):
    # 팝업 표시
```

## 결정 기준

- Streamlit 버전이 1.35 이상이고 on_select가 안정적으로 동작하면 **옵션 A** 선택
- 동작이 불안정하거나 버전 제약이 있으면 **옵션 B** 선택

## 결정 결과

> **[여기에 결정 내용을 기록한다]**
> 선택: 옵션 A / 옵션 B
> 이유:
> 결정일:
