# TASK-016 · Streamlit Community Cloud 배포 및 검증

| 항목 | 내용 |
|------|------|
| 상태 | waiting |
| 우선순위 | high |
| 예상 시간 | 30분 |
| 의존 | TASK-015 |

## 목표

GitHub 리포지토리를 Streamlit Community Cloud에 연결하고 Supabase Secrets를 설정하여 배포한다. 배포된 URL에서 핵심 사용자 흐름을 직접 확인한다.

## 완료 조건

- [ ] Streamlit Community Cloud에 앱 배포 완료
- [ ] 배포 URL에서 WIP Matrix가 정상 표시됨
- [ ] 셀 선택 → Lot 상세 팝업 흐름이 웹에서 동작함
- [ ] Supabase Secrets가 배포 환경에서 올바르게 주입됨
- [ ] `requirements.txt`의 모든 패키지가 정상 설치됨

## 배포 절차

1. [share.streamlit.io](https://share.streamlit.io) 접속 및 GitHub 연동
2. **New app** → Repository, Branch, Main file path (`app.py`) 설정
3. **Advanced settings → Secrets** 에 Supabase 정보 입력:
   ```toml
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "eyJ..."
   ```
4. **Deploy** 클릭 → 빌드 로그 확인
5. 배포 완료 후 URL 확인

## 배포 후 검증 체크리스트

- [ ] WIP Matrix 전체 데이터 정상 표시
- [ ] Product 필터 동작
- [ ] STEP 필터 동작
- [ ] Status/Hold 필터 동작
- [ ] 셀/selectbox 선택 시 Lot 상세 팝업 정상 오픈
- [ ] Hold Lot 강조 표시 확인
- [ ] 빈 조건 선택 시 안내 메시지 표시

## 주의사항

- GitHub에 `secrets.toml`이 포함되어 있지 않은지 배포 전 최종 확인
- 빌드 실패 시 Streamlit Cloud 로그에서 패키지 버전 충돌 여부 확인
- 배포 URL을 README.md에 추가하여 접근성을 높인다
