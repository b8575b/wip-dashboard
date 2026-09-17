# WIP 재공 현황판

품질 담당자가 제품별·공정 STEP별 재공(WIP) 수량을 Matrix 형태로 확인하고,
수량 선택 시 해당 Lot 상세정보를 팝업으로 조회하는 웹 기반 현황판.

## 배포 URL

**https://wip-dashboard-ehahzsaygprxfbkxakgeht.streamlit.app/**

## 주요 기능

- **WIP Matrix**: 제품(행) × 공정 STEP(열) 교차 수량 표
- **필터**: Product / STEP / Status / Hold Lot
- **Lot 상세 팝업**: Matrix 셀 클릭 → 해당 조건의 Lot 목록 조회
- **메트릭 카드**: 전체 WIP / Hold Lot 수 / 장시간 대기(24h+) 수

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 환경 설정

`.streamlit/secrets.toml` 파일을 생성하고 Supabase 접속 정보를 입력한다.

```toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

## 기술 스택

- Python 3.10 / Streamlit ≥ 1.35
- Supabase PostgreSQL
- Pandas / Plotly
