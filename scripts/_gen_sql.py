import csv

rows = []
with open("sources/rawdata.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append(r)

cols = (
    "id,product_name,step_order,step_name,lot_id,"
    "quantity,equipment,input_time,waiting_hours,status,hold_yn,created_at"
)
vals = []
for r in rows:
    vals.append(
        "({},{!r},{},{!r},{!r},{},{!r},{!r},{},{!r},{!r},{!r})".format(
            r["id"], r["product_name"], r["step_order"], r["step_name"],
            r["lot_id"], r["quantity"], r["equipment"],
            r["input_time"] + "+00", r["waiting_hours"],
            r["status"], r["hold_yn"], r["created_at"] + "+00",
        )
    )

sql = "INSERT INTO wip_inventory ({}) VALUES\n{};".format(cols, ",\n".join(vals))
with open("scripts/insert_data.sql", "w", encoding="utf-8") as f:
    f.write(sql)
print(f"생성 완료: {len(rows)}행")
