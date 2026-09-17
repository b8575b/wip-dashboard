# TASK-004 · CSV 데이터 Supabase에 적재

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-003 |

## 목표

`sources/rawdata.csv`를 읽어 Supabase `wip_inventory` 테이블에 일괄 insert하고 건수를 검증한다.

## 완료 조건

- [ ] 스크립트 실행 시 오류 없이 전체 행 insert 완료
- [ ] Supabase 콘솔 Table Editor에서 데이터 건수가 CSV 행 수와 일치
- [ ] 중복 실행 방지 처리 (이미 데이터가 있으면 skip 또는 경고)

## 작업 내용

일회성 적재 스크립트 `scripts/load_data.py`를 작성한다:

```python
import pandas as pd
from supabase import create_client
import toml, os

secrets = toml.load(".streamlit/secrets.toml")
client = create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_KEY"])

df = pd.read_csv("sources/rawdata.csv")
# input_time, created_at을 ISO 문자열로 변환
df["input_time"] = pd.to_datetime(df["input_time"]).dt.isoformat()
df["created_at"] = pd.to_datetime(df["created_at"]).dt.isoformat()

records = df.to_dict(orient="records")
response = client.table("wip_inventory").insert(records).execute()
print(f"Inserted: {len(response.data)} rows")
```

## 실행 방법

```bash
python scripts/load_data.py
```

## 주의사항

- 이 스크립트는 일회성 도구이므로 `app.py`에 포함하지 않는다
- 이미 데이터가 적재된 상태에서 재실행하면 중복 insert가 발생할 수 있으니 주의
