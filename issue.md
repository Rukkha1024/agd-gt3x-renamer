# Issue Tracking

## 🔧 Merge 후 확인 필요 사항

### Issue #1: `file_extensions` 설정 위치 변경
- **상태**: ⏳ 확인 필요
- **설명**: 
  - main branch: `config.yaml`에 `file_extensions` 정의
  - 현재 branch: `modify.py`에서 `FILE_EXTENSIONS` 상수로 정의 (config.yaml에서 삭제)
- **영향**: 기존 main branch의 config.yaml 사용 시 키 누락 에러 가능
- **해결 방안**: 현재 branch 방식 유지 (코드 내 상수 사용)
- **담당**: merge 후 테스트로 확인

---

## ✅ 완료된 이슈

(없음)
