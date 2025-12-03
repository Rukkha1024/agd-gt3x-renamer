# Progress 03 Implementation Plan: Excel 데이터 연동 설계

## 작업 개요

**목표**: Excel 데이터를 사용하여 .agd/.gt3x 파일의 메타데이터를 자동으로 수정하는 통합 워크플로우 설계

**현재 상태**:
- ✅ Progress 01: 메타데이터 차이점 분석 완료
- ✅ Progress 02: modify.py (메타데이터 수정 기능) 구현 완료
- ✅ name.py: 파일명 변경 기능 구현 완료
- 🎯 Progress 03: 두 기능을 통합하는 워크플로우 설계 (현재 작업)

---

## 핵심 설계 원칙

### 1. 데이터 매칭 전략

**현재 name.py의 매칭 로직 활용**:

```
파일명 (예: MOS2A50130052 (2025-12-02)60sec.agd)
    ↓ extract_serial_from_filename()
고유번호 (Serial Number: MOS2A50130052)
    ↓ get_management_number() [관리번호-시리얼번호.xlsx 사용]
관리번호 (Management Number: 12)
    ↓ get_subject_info() [대상자 키,체중,주손 정보.xlsx 사용]
대상자 정보 (ID, 이름, 착용시작일, 키, 체중, 성별, 주손 등)
    ↓
메타데이터 수정 + 파일명 변경
```

**핵심**: name.py의 기존 매칭 로직을 재사용하여 Excel 데이터를 추출

---

## 설계 상세

### Phase 1: 데이터 추출 및 매핑

#### 1.1 Excel 데이터 구조 분석

**파일**: `Archive/대상자 키,체중,주손 정보.xlsx`

| 컬럼명 | 용도 | 비고 |
|--------|------|------|
| 구분 | Division (예: "1주차", "40주차") | name.py --week 파라미터 |
| 관리번호 | Management Number | 매칭 키 |
| ID | Subject ID | 파일명 생성용 |
| 이름 | Subject Name | 파일명 + 메타데이터 |
| 성별 | Sex | 메타데이터 (남→Male, 여→Female) |
| 나이 | Age | 메타데이터 |
| 키 | Height | 메타데이터 |
| 체중 | Mass | 메타데이터 |
| 생년월일 | Date of Birth | 메타데이터 (YYYY-MM-DD → datetime → Ticks 변환) |
| 주손 | Handedness | 메타데이터 (오→Left+Dominant, 왼→Right+Non-Dominant) |
| 착용 시작일 | Wear Start Date | 파일명 생성용 |

#### 1.2 메타데이터 매핑 규칙

**Excel → .agd/.gt3x 메타데이터 변환**:

| Excel 컬럼 | .agd/.gt3x 필드 | 변환 규칙 |
|------------|-----------------|-----------|
| 이름 | subjectname | 직접 사용 |
| 성별 | sex | "남"→"Male", "여"→"Female" |
| 키 | height | int(키) |
| 체중 | mass | int(체중) |
| 나이 | age | int(나이) |
| 생년월일 | dateOfBirth | parse_date() → datetime_to_ticks() |
| 주손 | side, dominance | "오"→(Left, Dominant), "왼"→(Right, Non-Dominant) |
| (고정값) | limb | "Waist" |

**생년월일 변환 예시**:
- Excel: "1978-01-16" (YYYY-MM-DD 형식)
- 파싱: datetime(1978, 1, 16)
- Ticks 변환: datetime(1978, 1, 16) → Ticks

---

### Phase 2: 통합 워크플로우 설계

#### 2.1 전체 워크플로우

```
[입력]
├─ .agd/.gt3x 파일 (원본, 고유번호 포함)
├─ Excel: 관리번호-시리얼번호.xlsx
├─ Excel: 대상자 키,체중,주손 정보.xlsx
└─ 파라미터: --week 구분 (예: "40주차")

[처리 단계]
Step 1: 파일명에서 고유번호 추출
Step 2: 고유번호 → 관리번호 매핑
Step 3: 관리번호 + 구분 → Excel에서 대상자 전체 정보 조회
Step 4: Excel 데이터 → 메타데이터 형식 변환
Step 5: .agd 파일 메타데이터 수정 (modify.py)
Step 6: .gt3x 파일 메타데이터 수정 (modify.py)
Step 7: 파일명 변경 (name.py 로직)

[출력]
└─ 수정된 파일: ID_이름 (착용시작일).{agd,gt3x}
```

#### 2.2 데이터 플로우 다이어그램

```
ActiGraphRenamer (name.py)
    │
    ├─ load_data(year, division)
    │   ├─ serial_mapping_df (관리번호-시리얼번호.xlsx)
    │   └─ subject_info_df (대상자 키,체중,주손 정보.xlsx)
    │
    └─ process_file(filepath, division)
        │
        ├─ extract_serial_from_filename()
        ├─ get_management_number()
        ├─ get_subject_info() → (ID, 이름, 착용시작일)
        │
        └─ [NEW] extract_metadata_from_subject_info()
            │   → metadata dict for modify.py
            │
            ├─ ActiGraphModifier.modify_agd_file()
            ├─ ActiGraphModifier.modify_gt3x_file()
            └─ rename_file()
```

---

### Phase 3: 구현 계획 (Progress 04)

#### 3.1 파일 구조 (3개 파일 제한 준수)

**옵션 1: name.py 확장 (권장)**
- ✅ 기존 name.py를 확장하여 메타데이터 수정 기능 통합
- ✅ 단일 스크립트로 파일명 + 메타데이터 일괄 수정
- ✅ config.yaml 활용하여 중앙 관리

**파일 구성**:
1. **name.py** (수정): 파일명 변경 + 메타데이터 수정 통합
2. **modify.py** (유지): ActiGraphModifier 클래스 (import하여 사용)
3. **config.yaml** (수정): 메타데이터 매핑 설정 추가

**옵션 2: 새 통합 스크립트 생성**
- integrate.py (신규 생성)
- name.py, modify.py import하여 사용
- 3개 파일 제한 위반 가능성

**결론**: 옵션 1 (name.py 확장) 채택

#### 3.2 name.py 수정 사항

**추가할 메서드**:

```python
class ActiGraphRenamer:

    def extract_metadata_from_subject_info(self, management_number: int, division: str) -> Dict:
        """Excel에서 전체 메타데이터 추출

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
        # subject_info_df에서 행 조회
        # 컬럼별로 값 추출 및 변환
        # sex_mapping 적용 ("남"→"Male", "여"→"Female")
        # 생년월일 파싱 (parse_date_from_excel())
        # metadata dict 반환

    def parse_date_from_excel(self, date_value) -> datetime:
        """Excel 날짜 파싱

        Excel에서 날짜는 pandas에서 자동으로 datetime으로 읽힘
        만약 문자열이면 YYYY-MM-DD 형식으로 파싱

        Args:
            date_value: pandas datetime 또는 문자열 "YYYY-MM-DD"

        Returns:
            datetime 객체
        """
        # pandas datetime이면 그대로 반환
        # 문자열이면 pd.to_datetime() 또는 datetime.strptime() 사용
        # YYYY-MM-DD 형식 파싱

    def process_file_with_metadata(self, filepath: Path, division: str,
                                   modify_metadata: bool = True,
                                   dry_run: bool = False) -> Tuple[bool, str]:
        """파일명 변경 + 메타데이터 수정 통합 처리

        Args:
            modify_metadata: True이면 메타데이터도 수정, False면 파일명만
        """
        # 1. 기존 process_file() 로직 (파일명 변경)
        # 2. [NEW] 메타데이터 추출
        #    metadata = self.extract_metadata_from_subject_info(mgmt_num, division)
        # 3. [NEW] modify.py 호출
        #    modifier = ActiGraphModifier(self.config_path)
        #    modifier.modify_agd_file(filepath, metadata)
        #    modifier.modify_gt3x_file(filepath, metadata)
        # 4. [NEW] 검증
        #    modifier.validate_agd_modification()
        #    modifier.validate_gt3x_modification()
```

**수정할 메서드**:

```python
def run(self, division: str, year: int = None,
        modify_metadata: bool = True, dry_run: bool = False):
    """
    Args:
        modify_metadata: 메타데이터 수정 여부 (기본값: True)
    """
    # 기존 로직 유지
    # process_file() 대신 process_file_with_metadata() 호출
```

#### 3.3 config.yaml 수정 사항

**추가할 설정**:

```yaml
columns:
  subject_info:
    division: "구분"
    management_number: "관리번호"
    id: "ID"
    name: "이름"
    wear_start_date: "착용 시작일"
    # [NEW] 메타데이터용 컬럼
    sex: "성별"
    age: "나이"
    height: "키"
    mass: "체중"
    date_of_birth: "생년월일"
    handedness: "주손"

# 이미 존재 (Progress 02에서 추가됨)
metadata:
  sex_mapping:
    "남": "Male"
    "여": "Female"

  handedness_mapping:
    "오":  # 오른손잡이
      side: "Left"
      dominance: "Dominant"
    "왼":  # 왼손잡이
      side: "Right"
      dominance: "Non-Dominant"
```

---

### Phase 4: 실행 시나리오

#### 4.1 사용법 (Progress 04 구현 후)

**기본 사용 (파일명 + 메타데이터 모두 수정)**:
```bash
conda run -n module python name.py --week 40주차 --year 2025
```

**파일명만 변경 (기존 동작)**:
```bash
conda run -n module python name.py --week 40주차 --no-metadata
```

**Dry-run 모드**:
```bash
conda run -n module python name.py --week 40주차 --dry
```

#### 4.2 처리 순서

1. **파일 발견**: `target_directory`에서 .agd, .gt3x 파일 스캔
2. **각 파일별 처리**:
   ```
   파일: MOS2A50130052 (2025-12-02)60sec.agd

   ├─ 고유번호 추출: MOS2A50130052
   ├─ 관리번호 조회: 12
   ├─ Excel 데이터 조회 (관리번호=12, 구분=40주차):
   │   - ID: DB51016001
   │   - 이름: 김홍선
   │   - 성별: 여 → Female
   │   - 키: 140
   │   - 체중: 52
   │   - 나이: 46
   │   - 생년월일: 01-16-78 → 1978-01-16 → Ticks
   │   - 주손: 왼 → (Right, Non-Dominant)
   │   - 착용시작일: 2025-01-15
   │
   ├─ .agd 메타데이터 수정
   │   UPDATE settings SET subjectname='김홍선', sex='Female', ...
   │
   ├─ .gt3x 메타데이터 수정
   │   info.txt 업데이트: Subject Name: 김홍선, Sex: Female, ...
   │
   ├─ 파일명 변경
   │   MOS2A50130052 (2025-12-02)60sec.agd
   │   → DB51016001_김홍선 (2025-01-15)60sec.agd
   │
   └─ 검증
       ✅ 메타데이터 9개 필드 확인
       ✅ 파일명 형식 확인
   ```

3. **결과 요약**:
   ```
   ✅ 성공: 10개 파일
   ⏭️ 건너뜀: 2개 (이미 처리됨)
   ❌ 실패: 0개
   ```

---

## Progress 04 구현 시 고려사항

### 1. 에러 처리

**시나리오별 처리**:

| 에러 상황 | 처리 방법 |
|----------|----------|
| Excel 데이터 누락 | 해당 파일 건너뛰고 계속 진행, 경고 출력 |
| 생년월일 파싱 실패 | 기본값 사용 또는 건너뛰기 |
| 메타데이터 수정 실패 | 백업에서 복원, 파일명 변경 롤백 |
| 파일명 변경 실패 | 메타데이터는 유지, 오류 로그 |

### 2. 트랜잭션 보장

**원칙**: 파일당 전체 성공 또는 전체 롤백

```python
try:
    backup_agd = create_backup(file.agd)
    backup_gt3x = create_backup(file.gt3x)

    # 메타데이터 수정
    modify_agd()
    modify_gt3x()

    # 검증
    validate_agd()
    validate_gt3x()

    # 파일명 변경
    rename_file()

    # 백업 삭제
    delete_backups()

except Exception:
    # 롤백
    restore_backups()
    raise
```

### 3. 생년월일 파싱 로직

**Excel 날짜 형식**: Excel에서는 datetime으로 자동 읽힘, 또는 "YYYY-MM-DD" 문자열

**파싱 로직**:

```python
def parse_date_from_excel(self, date_value) -> datetime:
    """Excel 날짜 파싱

    pandas.read_excel()은 날짜 컬럼을 자동으로 datetime64로 읽음
    만약 문자열이면 pd.to_datetime()으로 파싱
    """
    if isinstance(date_value, pd.Timestamp):
        return date_value.to_pydatetime()
    elif isinstance(date_value, datetime.datetime):
        return date_value
    else:
        # 문자열인 경우 (YYYY-MM-DD 형식)
        return pd.to_datetime(date_value).to_pydatetime()
```

**간단한 처리**: pandas가 자동으로 날짜를 datetime으로 변환하므로 복잡한 파싱 로직 불필요

### 4. 검증 강화

**수정 후 검증 항목**:
- ✅ .agd 9개 필드 모두 Excel 값과 일치
- ✅ .gt3x 9개 필드 모두 Excel 값과 일치
- ✅ 파일명이 올바른 형식 (ID_이름 (착용시작일).확장자)
- ✅ 파일이 ActiLife에서 정상 열림 (수동 검증)

---

## 테스트 계획 (Progress 04)

### 1. 단위 테스트

```python
# test_metadata_extraction.py

def test_extract_metadata_from_excel():
    """Excel에서 메타데이터 추출 테스트"""
    renamer = ActiGraphRenamer()
    renamer.load_data(2025)

    metadata = renamer.extract_metadata_from_subject_info(
        management_number=12,
        division="1주차"
    )

    assert metadata['subjectname'] == '김홍선'
    assert metadata['sex'] == 'Female'
    assert metadata['height'] == 140
    assert metadata['mass'] == 52
    assert metadata['age'] == 46
    assert metadata['hand'] == '왼'
    # dateOfBirth는 datetime 객체

def test_parse_date_from_excel():
    """생년월일 파싱 테스트"""
    renamer = ActiGraphRenamer()

    # pandas Timestamp
    dt1 = renamer.parse_date_from_excel(pd.Timestamp("1978-01-16"))
    assert dt1 == datetime.datetime(1978, 1, 16)

    # 문자열 YYYY-MM-DD
    dt2 = renamer.parse_date_from_excel("2003-02-22")
    assert dt2 == datetime.datetime(2003, 2, 22)
```

### 2. 통합 테스트

```python
def test_full_workflow():
    """전체 워크플로우 테스트"""
    # Original 파일 복사
    shutil.copy("Archive/original_*.agd", "test/")
    shutil.copy("Archive/original_*.gt3x", "test/")

    # 실행
    renamer = ActiGraphRenamer()
    renamer.run(division="테스트", year=2025, dry_run=False)

    # 검증
    # 1. 메타데이터 확인
    # 2. 파일명 확인
    # 3. Modified 파일과 비교
```

---

## 파일 수정 요약

### 수정할 파일

| 파일 | 작업 | 상세 |
|------|------|------|
| **name.py** | 확장 | - `extract_metadata_from_subject_info()` 추가<br>- `parse_date_from_excel()` 추가<br>- `process_file_with_metadata()` 추가<br>- `run()` 메서드에 `--modify-metadata` 옵션 추가<br>- `from modify import ActiGraphModifier` import 추가 |
| **config.yaml** | 수정 | - `columns.subject_info`에 메타데이터 컬럼 추가 (sex, age, height, mass, date_of_birth, handedness) |
| **modify.py** | 유지 | - 변경 없음 (import되어 사용됨) |

### 새로 생성할 파일

| 파일 | 목적 |
|------|------|
| `progress/progress_03/progress_03.md` | 이 설계 문서를 progress 폴더에 기록 |

---

## 성공 기준

Progress 03 완료 조건:
- ✅ Excel 데이터 매칭 로직 명확히 정의
- ✅ 메타데이터 변환 규칙 명확히 정의
- ✅ name.py + modify.py 통합 방법 설계
- ✅ 생년월일 파싱 로직 설계
- ✅ 에러 처리 및 트랜잭션 전략 정의
- ✅ Progress 04 구현을 위한 명확한 가이드 제공

---

## 다음 단계 (Progress 04)

Progress 04에서 구현할 내용:
1. name.py에 메타데이터 추출 및 수정 기능 통합
2. config.yaml에 메타데이터 컬럼 매핑 추가
3. 생년월일 파싱 함수 구현
4. 통합 테스트 실행
5. Original 파일들로 실제 테스트
6. 결과 검증 및 문서화

**예상 사용 예시**:
```bash
# 40주차 파일 일괄 처리 (파일명 + 메타데이터)
conda run -n module python name.py --week 40주차 --year 2025

# Dry-run으로 미리보기
conda run -n module python name.py --week 40주차 --dry
```
