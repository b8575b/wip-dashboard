# WIP 재공 현황판

제품별·공정 STEP별 재공(WIP) 수량을 Matrix 형태로 확인하고, Lot 상세정보를 팝업으로 조회하는 웹 기반 대시보드.

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
