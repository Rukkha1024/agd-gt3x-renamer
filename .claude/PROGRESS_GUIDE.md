# Progress 폴더 가이드

## 개요

이 프로젝트는 **5단계 working progress**로 진행됩니다.
각 progress의 작업 내용과 결과는 `progress/` 폴더에 기록됩니다.

**AI Agent는 작업 시 항상 해당 progress 폴더를 참고해야 합니다.**

---

## Working Progress 전체 계획

```
progress/
├── progress_01/  ✅ 완료 (2025-12-03)
├── progress_02/  ⏳ 대기
├── progress_03/  ⏳ 대기
├── progress_04/  ⏳ 대기
└── progress_05/  ⏳ 대기
```

### Progress 01: Meta Information 차이점 분석 ✅
**목표**: Modified와 Original 파일 간의 메타데이터 차이점 찾기
**위치**: `progress/progress_01/`
**핵심 결과**:
- 6개 핵심 필드 식별 (subjectname, sex, height, mass, age, dateOfBirth)
- .agd 구조: SQLite Database (settings 테이블 수정)
- .gt3x 구조: ZIP Archive (info.txt만 수정, METADATA JSON 불필요)
- 손잡이 매핑 규칙 확인
- Ticks 변환 검증

### Progress 02: Original 파일 수정 및 검증
**목표**: 파이썬으로 Original 파일을 수정해 Modified와 동일하게 만들기
**위치**: `progress/progress_02/` (예정)
**필요 작업**:
1. .agd 파일 수정 함수 작성
2. .gt3x 파일 수정 함수 작성
3. 테스트 실행 및 검증
4. 사용자 컨펌

### Progress 03: 외부 데이터 연동 계획 수립
**목표**: Excel 데이터로 파일 수정하는 방법 계획 작성
**위치**: `progress/progress_03/` (예정)
**참고 파일**:
- `Archive/대상자 키,체중,주손 정보.xlsx`
- `name.py`, `config.yaml` (파일명 변경 로직)

### Progress 04: 자동화 스크립트 작성
**목표**: Progress 03 계획을 파이썬 코드로 구현
**위치**: `progress/progress_04/` (예정)

### Progress 05: 최종 실행 및 검증
**목표**: Original 파일들에 대해 파일명 변경 + 메타데이터 수정
**위치**: `progress/progress_05/` (예정)

---

## AI Agent 작업 시 규칙

### 1. Progress 폴더 참고 의무
**반드시 현재 progress와 이전 progress 폴더들을 참고해야 합니다.**

```python
# 예시: Progress 02 작업 시
- progress/progress_01/progress_01.md 읽기 (필수)
- progress/progress_01/의 분석 결과 활용
- progress/progress_02/ 폴더 생성 및 작업 기록
```

### 2. Progress 폴더 구조
각 progress 폴더는 다음 구조를 따릅니다:

```
progress/progress_XX/
├── progress_XX.md          # 작업 요약 및 핵심 결과
├── *.py                    # 작성한 스크립트들
├── *.json                  # 분석 결과 데이터
└── README.md 또는 기타 문서
```

### 3. Progress 문서 작성 규칙
각 `progress_XX.md`는 다음 내용을 포함해야 합니다:

1. **작업 개요**: 날짜, 상태, 목표
2. **핵심 발견 사항**: 중요한 결과 요약
3. **생성된 파일 목록**: 스크립트, 데이터 파일
4. **다음 단계**: 다음 progress를 위한 가이드
5. **AI Agent 참고 사항**: 후속 작업 시 주의사항

### 4. 작업 시작 전 체크리스트
- [ ] 현재 progress 번호 확인
- [ ] 이전 progress 폴더들 검토
- [ ] `progress_XX.md` 읽고 핵심 내용 파악
- [ ] 필요한 파일 경로 및 데이터 확인
- [ ] 작업 완료 후 새 progress 폴더에 기록

---

## 현재 상태 (2025-12-03)

### ✅ 완료된 작업
- **Progress 01**: Meta Information 차이점 분석 완료
  - 위치: `progress/progress_01/`
  - 핵심 파일: `progress_01.md` (전체 요약)

### 🎯 다음 작업
- **Progress 02**: Original 파일 수정 및 검증
  - 사용자 요청 대기 중
  - Progress 01 결과를 기반으로 수정 함수 작성 예정

---

## 중요 참고 사항

### 손잡이 매핑 규칙 ⚠️
| Excel (주손) | .agd/.gt3x (Side) | Dominance |
|-------------|-------------------|-----------|
| **오** | **Left** | **Dominant** |
| **왼** | **Right** | **Non-Dominant** |

### Ticks 변환
```python
# 예시: 1999-11-01 = 630770112000000000 Ticks
import datetime

def datetime_to_ticks(dt):
    base = datetime.datetime(1, 1, 1)
    delta = dt - base
    return int(delta.total_seconds() * 10_000_000)
```

### 파일 구조
- **.agd**: SQLite Database → `settings` 테이블 수정
- **.gt3x**: ZIP Archive → `info.txt` 수정 (METADATA JSON 불필요)

---

## 문의 및 확인

Progress 작업 관련 질문이 있거나 이전 작업 내용이 불명확할 경우:
1. 해당 `progress/progress_XX/progress_XX.md` 확인
2. 상세 문서 및 스크립트 검토
3. 사용자에게 질문

**항상 progress 폴더를 신뢰할 수 있는 단일 정보원(Single Source of Truth)으로 사용하세요.**
