import re
import sys
import pandas as pd
from supabase import create_client


def _load_secrets(path):
    secrets = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'(\w+)\s*=\s*"([^"]*)"', line.strip())
            if m:
                secrets[m.group(1)] = m.group(2)
    return secrets


def main():
    s = _load_secrets(".streamlit/secrets.toml")
    client = create_client(s["SUPABASE_URL"], s["SUPABASE_KEY"])

    existing = client.table("wip_inventory").select("id", count="exact").execute()
    if existing.count and existing.count > 0:
        print(f"이미 {existing.count}건 존재합니다. 적재를 건너뜁니다.")
        sys.exit(0)

    df = pd.read_csv("sources/rawdata.csv", encoding="utf-8-sig")
    for col in ("input_time", "created_at"):
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    total = len(records)

    inserted = 0
    for i in range(0, total, 500):
        resp = client.table("wip_inventory").insert(records[i:i + 500]).execute()
        inserted += len(resp.data)
        print(f"  {inserted}/{total} 완료")

    if inserted != total:
        print(f"경고: 건수 불일치 — 삽입 {inserted} / CSV {total}")
        sys.exit(1)
    print(f"적재 완료: {inserted}건")


if __name__ == "__main__":
    main()
