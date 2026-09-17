# TASK-007 · Product × STEP WIP 수량 집계 (Pandas pivot)

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-006 |

## 목표

조회한 DataFrame을 `product_name × step_name` 기준으로 `quantity`를 합산하여 Matrix용 pivot table을 생성한다. 열은 `step_order` 기준으로 정렬한다.

## 완료 조건

- [ ] `build_wip_matrix(df)` 함수 구현 완료
- [ ] 반환값이 행=product_name, 열=step_name(step_order 순), 값=quantity 합계인 DataFrame
- [ ] 수량이 없는 셀은 `0`으로 채워짐 (NaN 없음)
- [ ] 간단한 assert 또는 print로 결과 검증

## 작업 내용

```python
# data/aggregate.py
import pandas as pd

def build_wip_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    # step_order 기준 열 순서 확보
    step_order = (
        df[["step_name", "step_order"]]
        .drop_duplicates()
        .sort_values("step_order")["step_name"]
        .tolist()
    )

    matrix = df.pivot_table(
        index="product_name",
        columns="step_name",
        values="quantity",
        aggfunc="sum",
        fill_value=0
    )
    # step_order 순으로 열 정렬
    matrix = matrix.reindex(columns=step_order, fill_value=0)
    matrix.index.name = "Product"
    matrix.columns.name = None
    return matrix
```

## 예상 출력 형태

```
           STEP_010  STEP_020  STEP_030  STEP_040
Product
PRODUCT_A       109       164        95       245
PRODUCT_B        78       121       134       198
PRODUCT_C       102        87       156       224
```
