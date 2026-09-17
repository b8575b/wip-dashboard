-- wip_inventory 테이블 생성
CREATE TABLE IF NOT EXISTS wip_inventory (
    id            bigint PRIMARY KEY,
    product_name  text NOT NULL,
    step_order    integer NOT NULL,
    step_name     text NOT NULL,
    lot_id        text NOT NULL,
    quantity      integer NOT NULL,
    equipment     text,
    input_time    timestamp,
    waiting_hours numeric(6, 1),
    status        text,
    hold_yn       text,
    created_at    timestamp DEFAULT now()
);

-- RLS 활성화 (supabase 스킬 보안 원칙)
ALTER TABLE wip_inventory ENABLE ROW LEVEL SECURITY;

-- anon 역할에 SELECT 허용 (데모용 대시보드)
CREATE POLICY "anon_select" ON wip_inventory
    FOR SELECT
    TO anon
    USING (true);

-- Data API 노출용 GRANT
GRANT SELECT ON wip_inventory TO anon;
GRANT SELECT ON wip_inventory TO authenticated;
