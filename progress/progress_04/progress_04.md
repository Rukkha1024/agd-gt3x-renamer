# Progress 04: Excel 데이터 연동 및 메타데이터 수정 기능 구현 완료

**작업 날짜**: 2025-12-03
**상태**: ✅ 완료
**목표**: Progress 03 계획을 파이썬 코드로 구현하여 Excel 데이터로 메타데이터 자동 수정

---

## 1. 작업 개요

Progress 03에서 설계한 통합 워크플로우를 name.py에 구현하여, Excel 데이터를 기반으로 .agd/.gt3x 파일의 메타데이터를 자동으로 수정하고 파일명을 변경하는 기능을 완성했습니다.

**핵심 목표:**
- name.py에 메타데이터 추출 및 수정 기능 통합
- Excel 생년월일 파싱 (MM-DD-YY 형식)
- 파일명 변경 + 메타데이터 수정 일괄 처리
- 3개 파일 제한 준수 (name.py + modify.py + config.yaml)

---

## 2. 구현 내용

### 2.1 수정된 파일

| 파일 | 유형 | 설명 |
|------|------|------|
| **name.py** | 확장 | 메타데이터 추출 및 수정 기능 추가 (3개 메서드 추가) |
| **config.yaml** | 업데이트 | 메타데이터 컬럼 매핑 추가 (성별, 나이, 키, 체중, 생년월일, 주손) |
| **modify.py** | 유지 | 변경 없음 (import하여 사용) |

### 2.2 name.py에 추가된 메서드

#### 2.2.1 parse_date_from_excel()

**목적**: Excel의 생년월일을 datetime으로 변환

```python
def parse_date_from_excel(self, date_value) -> Optional[datetime.datetime]:
    """Excel 날짜 파싱 (MM-DD-YY 형식)

    Example:
        "01-16-78" -> datetime(1978, 1, 16)
        "02-22-03" -> datetime(2003, 2, 22)

    Note:
        YY < 50 -> 20YY (2000년대)
        YY >= 50 -> 19YY (1900년대)
    """
```

**주요 로직:**
1. pandas Timestamp → datetime 변환
2. 문자열 "MM-DD-YY" 파싱
3. 2자리 연도를 4자리로 변환 (50년 기준)
4. 에러 처리 및 None 반환

**테스트 결과:**
- ✅ "01-16-78" → 1978-01-16 → Ticks: 623893536000000000
- ✅ Ticks 역변환 검증 완료

#### 2.2.2 extract_metadata_from_subject_info()

**목적**: Excel에서 전체 메타데이터 추출

```python
def extract_metadata_from_subject_info(self, management_number: int, division: str) -> Optional[Dict]:
    """Excel에서 메타데이터 추출

    Returns:
        {
            'subjectname': str,
            'sex': str,  # "Male" or "Female"
            'height': int,
            'mass': int,
            'age': int,
            'dateOfBirth': datetime,
            'hand': str,  # "오" or "왼"
            'limb': str   # "Waist"
        }
    """
```

**주요 로직:**
1. config.yaml에서 컬럼명 읽기
2. Excel에서 관리번호 + 구분으로 행 조회
3. 생년월일 파싱 (parse_date_from_excel 호출)
4. 성별 매핑 ("남"→"Male", "여"→"Female")
5. 메타데이터 dict 구성 및 반환

**테스트 결과:**
- ✅ 관리번호 12, 1주차 → 김홍선 데이터 추출 성공
- ✅ 모든 필드 정확히 매핑

#### 2.2.3 process_file() 메서드 확장

**변경 사항:**
- `modify_metadata` 파라미터 추가 (기본값: True)
- 메타데이터 수정 로직 추가 (파일명 변경 전)
- ActiGraphModifier import 및 사용
- 검증 로직 추가 (9개 필드 모두 검증)

**워크플로우:**
```
1. 고유번호 추출 → 관리번호 조회 → Excel 데이터 조회
2. [NEW] 메타데이터 추출 (extract_metadata_from_subject_info)
3. [NEW] .agd 또는 .gt3x 메타데이터 수정 (modify.py 호출)
4. [NEW] 검증 (validate_*_modification)
5. 파일명 변경
```

**에러 처리:**
- 메타데이터 추출 실패 → 해당 파일 건너뛰기
- 메타데이터 수정 실패 → 백업 복원 (modify.py 내장)
- 검증 실패 → 오류 반환

### 2.3 config.yaml 추가 내용

```yaml
columns:
  subject_info:
    division: "구분"
    management_number: "관리번호"
    id: "ID"
    name: "이름"
    wear_start_date: "착용 시작일"
    # 메타데이터 추가 컬럼 (Progress 04)
    sex: "성별"
    age: "나이"
    height: "키"
    mass: "체중"
    date_of_birth: "생년월일"
    handedness: "주손"
```

### 2.4 argparse 업데이트

**추가된 플래그:**
```python
--no-metadata: 메타데이터 수정 없이 파일명만 변경
```

**사용 예시:**
```bash
# 기본: 메타데이터 + 파일명 모두 수정
conda run -n module python name.py --week 40주차 --year 2025

# Dry-run 모드
conda run -n module python name.py --week 40주차 --dry

# 파일명만 변경 (메타데이터 수정 안함)
conda run -n module python name.py --week 40주차 --no-metadata
```

---

## 3. 테스트 결과

### 3.1 테스트 환경

**대상자:** 김홍선 (관리번호 12, 1주차)

**Excel 데이터:**
```
- ID: DB51016001
- 이름: 김홍선
- 성별: 여 → Female
- 나이: 46
- 키: 140
- 체중: 52
- 생년월일: 01-16-78 → 1978-01-16
- 주손: 왼 → (Right, Non-Dominant)
```

**테스트 파일:**
- Input: `temp_test/MOS2A50130066 (2025-01-15)60sec.{agd,gt3x}`
- Output: `temp_test/DB51016001_김홍선 (2025-01-15)60sec.{agd,gt3x}`

### 3.2 테스트 1: Dry-run 모드

**실행 명령:**
```bash
conda run -n module python name.py --week 1주차 --year 2025 --dry
```

**결과:**
```
============================================================
ActiGraph 파일 자동 이름 변경
============================================================
📅 연도: 2025
📌 구분: 1주차
🔍 모드: DRY-RUN (미리보기)
📝 메타데이터 수정: 예
============================================================

✅ [DRY-RUN] 메타데이터 + 파일명: MOS2A50130066 (2025-01-15)60sec.agd -> DB51016001_김홍선 (2025-01-15)60sec.agd
✅ [DRY-RUN] 메타데이터 + 파일명: MOS2A50130066 (2025-01-15)60sec.gt3x -> DB51016001_김홍선 (2025-01-15)60sec.gt3x

============================================================
📊 처리 결과
============================================================
✅ 성공: 2개
⏭️  건너뜀: 0개
❌ 실패: 0개
============================================================
```

**결론:** ✅ Dry-run 모드 정상 동작

### 3.3 테스트 2: 실제 실행 (메타데이터 + 파일명)

**실행 명령:**
```bash
conda run -n module python name.py --week 1주차 --year 2025
```

**결과:**
```
✅ 변경 완료 (메타데이터 + 파일명): MOS2A50130066 (2025-01-15)60sec.agd -> DB51016001_김홍선 (2025-01-15)60sec.agd
✅ 변경 완료 (메타데이터 + 파일명): MOS2A50130066 (2025-01-15)60sec.gt3x -> DB51016001_김홍선 (2025-01-15)60sec.gt3x

============================================================
📊 처리 결과
============================================================
✅ 성공: 2개
⏭️  건너뜀: 0개
❌ 실패: 0개
============================================================
```

**결론:** ✅ 메타데이터 + 파일명 변경 성공

### 3.4 테스트 3: .agd 파일 메타데이터 검증

**검증 명령:**
```python
import sqlite3
conn = sqlite3.connect('temp_test/DB51016001_김홍선 (2025-01-15)60sec.agd')
settings = dict(conn.execute('SELECT settingName, settingValue FROM settings').fetchall())
```

**결과:**

| 필드 | Excel 값 | .agd 값 | 일치 |
|------|---------|---------|------|
| subjectname | 김홍선 | 김홍선 | ✅ |
| sex | 여 → Female | Female | ✅ |
| height | 140 | 140 | ✅ |
| mass | 52 | 52 | ✅ |
| age | 46 | 46 | ✅ |
| dateOfBirth | 01-16-78 → 1978-01-16 | 623893536000000000 (Ticks) | ✅ |
| side | 왼 → Right | Right | ✅ |
| dominance | 왼 → Non-Dominant | Non-Dominant | ✅ |
| limb | (기본값) | Waist | ✅ |

**결론:** ✅ .agd 파일 9개 필드 모두 정확히 수정됨

### 3.5 테스트 4: .gt3x 파일 메타데이터 검증

**검증 명령:**
```python
import zipfile
with zipfile.ZipFile('temp_test/DB51016001_김홍선 (2025-01-15)60sec.gt3x', 'r') as zf:
    info_txt = zf.read('info.txt').decode('utf-8')
```

**결과:**

| 필드 | Excel 값 | .gt3x 값 | 일치 |
|------|---------|---------|------|
| Subject Name | 김홍선 | 김홍선 | ✅ |
| Sex | 여 → Female | Female | ✅ |
| Height | 140 | 140 | ✅ |
| Mass | 52 | 52 | ✅ |
| Age | 46 | 46 | ✅ |
| DateOfBirth | 01-16-78 → 1978-01-16 | 623893536000000000 (Ticks) | ✅ |
| Side | 왼 → Right | Right | ✅ |
| Dominance | 왼 → Non-Dominant | Non-Dominant | ✅ |
| Limb | (기본값) | Waist | ✅ |

**결론:** ✅ .gt3x 파일 9개 필드 모두 정확히 수정됨

### 3.6 테스트 5: 생년월일 Ticks 변환 정확성 검증

**검증 로직:**
```python
import datetime

# Excel "01-16-78" → 1978-01-16
expected_dob = datetime.datetime(1978, 1, 16)

# Ticks 변환
base = datetime.datetime(1, 1, 1)
delta = expected_dob - base
expected_ticks = int(delta.total_seconds() * 10_000_000)

print(f'기대값: {expected_dob} -> {expected_ticks} Ticks')
print(f'실제값: 623893536000000000 Ticks')
print(f'일치 여부: {expected_ticks == 623893536000000000}')
```

**결과:**
```
기대값: 1978-01-16 00:00:00 -> 623893536000000000 Ticks
실제값: 623893536000000000 Ticks
일치 여부: True
역변환: 623893536000000000 Ticks -> 1978-01-16 00:00:00
```

**결론:** ✅ 생년월일 변환 및 역변환 모두 정확

---

## 4. 핵심 구현 세부사항

### 4.1 Excel 생년월일 파싱 로직

**문제:** Excel에 "MM-DD-YY" 형식으로 저장된 날짜 파싱

**해결:**
```python
def parse_date_from_excel(self, date_value):
    # 문자열인 경우 (MM-DD-YY)
    date_str = str(date_value).strip()
    parts = date_str.split('-')
    month, day, year = int(parts[0]), int(parts[1]), int(parts[2])

    # 2자리 연도를 4자리로 변환
    if year < 50:
        year += 2000  # 00-49 → 2000-2049
    else:
        year += 1900  # 50-99 → 1950-1999

    return datetime.datetime(year, month, day)
```

**검증:**
- "01-16-78" → 1978 (1900 + 78)
- "02-22-03" → 2003 (2000 + 3)

### 4.2 메타데이터 수정 및 검증 플로우

```python
# 1. 메타데이터 추출
metadata = self.extract_metadata_from_subject_info(management_number, division)

# 2. ActiGraphModifier 초기화
modifier = ActiGraphModifier('config.yaml')

# 3. 파일 확장자에 따라 수정
if file_ext == '.agd':
    modifier.modify_agd_file(str(filepath), metadata)
elif file_ext == '.gt3x':
    modifier.modify_gt3x_file(str(filepath), metadata)

# 4. 검증 (9개 필드)
expected = {
    'subjectname': metadata['subjectname'],
    'sex': metadata['sex'],
    'height': metadata['height'],
    'mass': metadata['mass'],
    'age': metadata['age'],
    'dateOfBirth': metadata['dateOfBirth'],
    'side': modifier.map_handedness(metadata['hand'])[0],
    'dominance': modifier.map_handedness(metadata['hand'])[1],
    'limb': metadata['limb']
}

if file_ext == '.agd':
    modifier.validate_agd_modification(str(filepath), expected)
```

### 4.3 에러 처리 전략

| 상황 | 처리 방법 |
|------|----------|
| 메타데이터 추출 실패 | 해당 파일 건너뛰고 계속 진행, 오류 메시지 출력 |
| 생년월일 파싱 실패 | None 반환, 해당 파일 건너뛰기 |
| 메타데이터 수정 실패 | modify.py의 백업 복원 메커니즘 활용 |
| 검증 실패 | 오류 반환, 처리 중단 |
| 파일명 변경 실패 | 오류 메시지 출력 |

**트랜잭션 보장:**
- modify.py가 자동으로 백업 생성 및 복원
- 메타데이터 수정 → 검증 → 파일명 변경 순서로 진행
- 중간 단계 실패 시 이전 상태로 복원

---

## 5. 사용 가이드

### 5.1 기본 사용법

```bash
# 기본: 메타데이터 + 파일명 모두 수정
conda run -n module python name.py --week 40주차 --year 2025

# Dry-run으로 미리보기
conda run -n module python name.py --week 40주차 --dry

# 파일명만 변경 (기존 동작)
conda run -n module python name.py --week 40주차 --no-metadata

# 다른 연도
conda run -n module python name.py --week 1주차 --year 2024
```

### 5.2 처리 과정

```
1. Excel 데이터 로드 (관리번호-시리얼번호.xlsx, 대상자 정보.xlsx)
2. target_directory에서 .agd, .gt3x 파일 스캔
3. 각 파일별로:
   a. 고유번호 추출 (예: MOS2A50130066)
   b. 관리번호 조회 (예: 12)
   c. Excel에서 전체 메타데이터 조회 (관리번호 + 구분)
   d. .agd 메타데이터 수정
   e. .gt3x 메타데이터 수정
   f. 검증 (9개 필드)
   g. 파일명 변경
4. 결과 요약 출력
```

### 5.3 출력 예시

```
============================================================
ActiGraph 파일 자동 이름 변경
============================================================
📅 연도: 2025
📌 구분: 40주차
🔍 모드: 실제 변경
📝 메타데이터 수정: 예
============================================================

📂 데이터 로드 중...
  ✓ 관리번호-시리얼번호 매칭: 126 건
  ✓ 대상자 정보 (2025년): 1037 건
📁 발견된 파일: 10개

✅ 변경 완료 (메타데이터 + 파일명): MOS2A50130066 (2025-01-15)60sec.agd -> DB51016001_김홍선 (2025-01-15)60sec.agd
✅ 변경 완료 (메타데이터 + 파일명): MOS2A50130066 (2025-01-15)60sec.gt3x -> DB51016001_김홍선 (2025-01-15)60sec.gt3x
...

============================================================
📊 처리 결과
============================================================
✅ 성공: 10개
⏭️  건너뜀: 0개
❌ 실패: 0개
============================================================
```

---

## 6. 파일 구조 (3개 파일 제한 준수)

| 파일 | 역할 | 라인 수 |
|------|------|---------|
| **name.py** | 파일명 변경 + 메타데이터 수정 통합 | ~520 lines |
| **modify.py** | 메타데이터 수정 로직 (Progress 02) | ~660 lines |
| **config.yaml** | 중앙 설정 관리 | ~80 lines |

**총 파일 수**: 3개 (제한 준수 ✅)

---

## 7. 핵심 발견 사항

### 7.1 Excel 날짜 형식

**문제:** Excel의 "MM-DD-YY" 형식 (예: "01-16-78")

**해결:**
- 2자리 연도를 4자리로 변환 (50년 기준)
- YY < 50 → 2000년대, YY >= 50 → 1900년대
- datetime으로 변환 후 Ticks 변환

### 7.2 성별 및 손잡이 매핑

**성별:**
- Excel: "남", "여"
- .agd/.gt3x: "Male", "Female"
- config.yaml의 sex_mapping 활용

**손잡이:**
- Excel: "오" (오른손잡이), "왼" (왼손잡이)
- .agd/.gt3x: side + dominance
- config.yaml의 handedness_mapping 활용
- modify.py의 map_handedness() 메서드 활용

### 7.3 메타데이터 수정 순서의 중요성

**올바른 순서:**
1. 메타데이터 수정 (파일명 변경 전)
2. 검증
3. 파일명 변경

**이유:**
- 파일명을 먼저 변경하면 filepath 참조가 깨짐
- 메타데이터 수정 중 오류 발생 시 파일명은 원래대로 유지

### 7.4 config.yaml 중앙 관리의 장점

**통합된 설정:**
- Excel 파일 경로
- Excel 컬럼명
- 메타데이터 필드 매핑
- 성별/손잡이 매핑 규칙
- 기본값 (연도, limb 등)

**이점:**
- 코드 수정 없이 설정만 변경 가능
- 코드 재사용성 향상
- 유지보수 용이

---

## 8. 성공 기준 달성 여부

Progress 04 완료 조건:

- ✅ name.py에 메타데이터 추출 및 수정 기능 통합
- ✅ config.yaml에 메타데이터 컬럼 매핑 추가
- ✅ Excel 생년월일 파싱 함수 구현 (MM-DD-YY → datetime)
- ✅ 통합 워크플로우 구현 (메타데이터 + 파일명)
- ✅ --no-metadata 플래그 추가
- ✅ Dry-run 모드 정상 동작
- ✅ .agd 파일 9개 필드 검증 성공
- ✅ .gt3x 파일 9개 필드 검증 성공
- ✅ 생년월일 Ticks 변환 정확성 검증
- ✅ 에러 처리 및 백업 시스템 활용
- ✅ 3개 파일 제한 준수

**결론**: 모든 성공 기준 달성 ✅

---

## 9. 다음 단계 (Progress 05)

**목표:** 실제 Original 파일들에 대해 대량 처리 실행 및 최종 검증

**필요 작업:**
1. config.yaml의 target_directory를 실제 Original 파일 경로로 변경
2. 백업 생성 (전체 파일 복사)
3. Dry-run으로 미리보기 및 확인
4. 실제 실행
5. 결과 검증 (샘플링)
6. ActiLife에서 수동 검증
7. 최종 결과 문서화

**예상 사용 예시:**
```bash
# 1주차 파일 일괄 처리
conda run -n module python name.py --week 1주차 --year 2025

# 40주차 파일 일괄 처리
conda run -n module python name.py --week 40주차 --year 2025
```

---

## 10. AI Agent 참고 사항

**Progress 04 폴더를 참고할 때:**

1. **name.py 사용법:**
   - Excel 데이터로 메타데이터 자동 수정 기능 완성
   - `--week` 파라미터로 구분 지정 (필수)
   - `--year` 파라미터로 연도 지정 (선택, 기본값: config.yaml)
   - `--dry` 플래그로 미리보기
   - `--no-metadata` 플래그로 파일명만 변경

2. **Excel 데이터 구조:**
   - 생년월일: "MM-DD-YY" 형식 (예: "01-16-78")
   - 성별: "남", "여"
   - 주손: "오", "왼"
   - 구분: "1주차", "40주차" 등

3. **메타데이터 매핑:**
   - config.yaml의 sex_mapping, handedness_mapping 활용
   - modify.py의 map_handedness() 메서드 활용
   - Ticks 변환은 modify.py의 datetime_to_ticks() 활용

4. **주의사항:**
   - Excel에 구분이 NaN인 데이터는 매칭 불가
   - 고유번호가 관리번호-시리얼번호.xlsx에 없으면 실패
   - 관리번호 + 구분이 대상자 정보.xlsx에 없으면 실패
   - 메타데이터 수정은 파일명 변경 전에 수행

5. **검증 방법:**
   - SQLite로 .agd 파일 settings 테이블 확인
   - ZIP으로 .gt3x 파일 info.txt 확인
   - Ticks 변환 정확성 검증
   - ActiLife에서 수동 검증 권장

**성공 기준:**
- ✅ 통합 워크플로우 구현 완료
- ✅ 모든 테스트 통과
- ✅ 메타데이터 9개 필드 정확히 수정
- ✅ 파일명 변경 성공
- ✅ 3개 파일 제한 준수
- ✅ Progress 05 준비 완료

**다음 작업:** Progress 05에서 실제 Original 파일들에 대해 대량 처리 및 최종 검증
