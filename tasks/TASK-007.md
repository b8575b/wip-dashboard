# TASK-007 · Product × STEP WIP 수량 집계 (Pandas pivot)

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-006 |

## 쉬운 설명

조회된 WIP 데이터를 제품과 공정 STEP별로 정리하여 표 형태(행렬)로 만드는 단계입니다. 마치 창고에서 "PRODUCT_A의 STEP_010 재공량은 109개"처럼 제품별로 각 STEP에서의 총 수량을 한눈에 볼 수 있는 요약표를 만드는 것입니다. Pandas의 pivot 기능을 사용해서 원본 데이터의 행들을 행(제품)과 열(STEP)로 재배치하고, 중복된 데이터는 합산합니다. 이 단계가 완성되면 대시보드에 WIP 현황판이 표시될 수 있습니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `data/aggregate.py` | 기존 파일 | `build_wip_matrix(df)` 함수 구현 — DataFrame을 pivot하여 product × step 행렬 생성 |
| `data/fetch.py` | 기존 파일 | WIP 데이터 조회 — `fetch_wip_data()`의 반환값이 이 태스크의 입력 DataFrame |
| `app.py` | 기존 파일 | UI 진입점 — 대시보드에서 matrix를 표시하는 위치 (TASK-008에서 활용) |
| `sources/rawdata.csv` | 참조 파일 | 테스트 데이터 — 개발 중 matrix 형식 검증용 |

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
