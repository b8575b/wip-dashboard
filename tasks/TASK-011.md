# TASK-011 · 선택된 조건의 Lot 상세정보 조회

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-006, TASK-010 |

## 쉬운 설명

사용자가 현황판에서 특정 제품과 공정 STEP을 선택하면, 그 조건에 해당하는 모든 Lot(작업 배치)들의 상세 정보를 데이터베이스에서 조회하는 함수를 만드는 작업입니다. 각 Lot의 수량, 설비, 투입 시간, 대기 시간, 상태 등을 시간이 오래된 순으로 정렬해서 보여주므로, 품질 담당자가 어느 Lot이 가장 오래 기다리고 있는지 한눈에 파악할 수 있습니다.

## 관련 파일

| 파일 경로 | 상태 | 이 태스크에서의 역할 |
|-----------|------|---------------------|
| `data/fetch.py` | 기존 파일 | 이 태스크의 주요 산출 위치 — `fetch_lot_detail()` 함수 추가 |
| `db.py` | 기존 파일 | Supabase 클라이언트 초기화 — `get_client()` 호출 |
| `sources/rawdata.csv` | 데이터 파일 | 테스트 데이터 기준 — lot_id, product_name, step_name, waiting_hours 등의 컬럼 구조 |
| `app.py` | 기존 파일 | 이 함수의 소비처 — Product/STEP 선택 후 Lot 상세 팝업 표시 위치 (TASK-012) |
| `data/aggregate.py` | 기존 파일 | 참조 — WIP Matrix 집계 로직 이해 목적 |

## 목표

선택된 `product_name` + `step_name` 조건으로 해당 Lot 목록을 조회하는 함수를 작성한다.

## 완료 조건

- [ ] `fetch_lot_detail(product, step)` 함수 구현 완료
- [ ] 반환 DataFrame에 필수 컬럼 9개 포함
- [ ] 결과가 없을 때 빈 DataFrame 반환 (오류 없음)
- [ ] `waiting_hours`가 높은 순으로 정렬

## 필수 반환 컬럼

| 컬럼 | 표시명 |
|------|--------|
| `lot_id` | Lot ID |
| `product_name` | Product |
| `step_name` | STEP |
| `quantity` | 수량 |
| `equipment` | 설비 |
| `input_time` | 투입 시간 |
| `waiting_hours` | 대기 시간(h) |
| `status` | 상태 |
| `hold_yn` | Hold |

## 작업 내용

```python
# data/fetch.py 에 추가
def fetch_lot_detail(product: str, step: str) -> pd.DataFrame:
    client = get_client()
    response = (
        client.table("wip_inventory")
        .select("lot_id,product_name,step_name,quantity,equipment,input_time,waiting_hours,status,hold_yn")
        .eq("product_name", product)
        .eq("step_name", step)
        .order("waiting_hours", desc=True)
        .execute()
    )
    if not response.data:
        return pd.DataFrame()
    df = pd.DataFrame(response.data)
    df["input_time"] = pd.to_datetime(df["input_time"])
    return df
```

## 주의사항

- 이 함수는 사용자 선택마다 실행되므로 `st.cache_data` 없이 매번 조회한다 (최신 데이터 반영)
- 필요 시 `ttl=60` 정도로 단기 캐싱 적용 가능
