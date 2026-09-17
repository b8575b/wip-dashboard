# TASK-003 · Supabase 프로젝트 생성 및 테이블 스키마 설계

| 항목 | 내용 |
|------|------|
| 상태 | todo |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-001 |

## 목표

Supabase 콘솔에서 프로젝트를 생성하고 `wip_inventory` 테이블을 `rawdata.csv` 컬럼 구조에 맞게 정의한다.

## 완료 조건

- [ ] Supabase 프로젝트 생성 완료
- [ ] `wip_inventory` 테이블 생성 (아래 스키마 적용)
- [ ] Supabase URL 및 `anon` API Key 확보
- [ ] `.streamlit/secrets.toml`에 URL, Key 기재 (로컬에만 보관)

## 테이블 스키마

```sql
CREATE TABLE wip_inventory (
  id            bigint PRIMARY KEY,
  product_name  text NOT NULL,
  step_order    integer NOT NULL,
  step_name     text NOT NULL,
  lot_id        text NOT NULL,
  quantity      integer NOT NULL,
  equipment     text,
  input_time    timestamp,
  waiting_hours numeric(6,1),
  status        text,          -- RUN / WAIT / HOLD
  hold_yn       text,          -- Y / N
  created_at    timestamp
);
```

## secrets.toml 형식

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

## 주의사항

- Row Level Security(RLS)가 기본 활성화되어 있으면 anon key로 SELECT가 막힌다. 테스트 단계에서는 RLS를 비활성화하거나 SELECT 정책을 추가한다.
- API Key는 절대 GitHub에 커밋하지 않는다.
