# Progress 02: Original 파일 수정 및 검증 완료

**작업 날짜**: 2025-12-03
**상태**: ✅ 완료
**목표**: 파이썬으로 Original 파일을 수정해 Modified와 동일하게 만들기

---

## 1. 작업 개요

Progress 01에서 분석한 메타데이터 차이점을 기반으로, `.agd` 및 `.gt3x` 파일의 메타데이터를 프로그래밍 방식으로 수정하는 코드를 작성하고 검증했습니다.

**핵심 목표:**
- Original 파일을 수정하여 Modified 파일과 완벽히 일치시키기
- Progress 04에서 재사용 가능한 코드 작성
- 3개 파일 제한 준수 (modify.py + config.yaml 업데이트)

---

## 2. 구현 내용

### 2.1 생성/수정된 파일

| 파일 | 유형 | 설명 |
|------|------|------|
| **modify.py** | 신규 생성 | ActiGraphModifier 클래스 및 메타데이터 수정 로직 |
| **config.yaml** | 업데이트 | metadata 섹션 추가 (필드 매핑, 손잡이 매핑 등) |

### 2.2 ActiGraphModifier 클래스 구조

```python
class ActiGraphModifier:
    # 핵심 수정 메서드
    - modify_agd_file(file_path, metadata) -> bool
    - modify_gt3x_file(file_path, metadata) -> bool

    # 헬퍼 메서드
    - datetime_to_ticks(dt) -> int
    - ticks_to_datetime(ticks) -> datetime
    - map_handedness(hand) -> (side, dominance)
    - _parse_info_txt(content) -> dict
    - _update_info_txt(content, metadata) -> str
    - _create_backup(file_path) -> str
    - _restore_backup(original_path, backup_path)

    # 검증 메서드
    - validate_agd_modification(file_path, expected) -> bool
    - validate_gt3x_modification(file_path, expected) -> bool
```

### 2.3 config.yaml 추가 사항

```yaml
metadata:
  # .agd 파일 필드명 (SQLite settings 테이블)
  agd_fields:
    subjectname: "subjectname"
    sex: "sex"
    # ... 9개 필드

  # .gt3x 파일 필드명 (info.txt)
  gt3x_fields:
    subjectname: "Subject Name"
    sex: "Sex"
    # ... 9개 필드 (대소문자 다름)

  # 성별 매핑
  sex_mapping:
    "남": "Male"
    "여": "Female"

  # 손잡이 매핑 (주손의 반대편 손목에 착용)
  handedness_mapping:
    "오":  # 오른손잡이 → 왼쪽 손목
      side: "Left"
      dominance: "Dominant"
    "왼":  # 왼손잡이 → 오른쪽 손목
      side: "Right"
      dominance: "Non-Dominant"

  defaults:
    limb: "Waist"
```

---

## 3. 구현 세부사항

### 3.1 .agd 파일 수정 (SQLite)

**방법:**
1. 파일 백업 생성 (.agd.bak)
2. SQLite 데이터베이스 연결
3. settings 테이블 UPDATE
   ```sql
   UPDATE settings SET settingValue=? WHERE settingName=?
   ```
4. dateOfBirth를 Ticks로 변환
5. hand ("오"/"왼")를 side/dominance로 변환
6. 커밋 및 종료
7. 백업 삭제 (성공 시) 또는 복원 (실패 시)

**주요 발견:**
- 모든 값이 문자열로 저장됨 (숫자도 str() 변환 필요)
- 9개 필드 모두 settings 테이블에 존재

### 3.2 .gt3x 파일 수정 (ZIP Archive)

**방법:**
1. 파일 백업 생성
2. ZIP 압축 해제 (임시 디렉토리)
3. info.txt 읽기 및 파싱
4. 기존 필드 업데이트 + 없는 필드 삽입
   - **Sex, Height, Mass, Age**: "Acceleration Max" 다음에 삽입
   - **DateOfBirth**: "Dominance" 다음에 삽입
5. 수정된 info.txt로 ZIP 재생성
6. 백업 삭제/복원

**중요 발견:**
- Original 파일에는 Sex, Height, Mass, Age, DateOfBirth가 **없음**
- Modified 파일에는 이 필드들이 **추가됨** (특정 위치에)
- log.bin은 수정하지 않음 (Progress 01 확인 사항)

**info.txt 필드 삽입 위치:**
```
...
Acceleration Max: 8.0
Sex: Male              ← 삽입
Height: 177            ← 삽입
Mass: 70               ← 삽입
Age: 26                ← 삽입
Race: Asian / Pacific Islander
Limb: Waist
Side: Left
Dominance: Dominant
DateOfBirth: 630770112000000000  ← 삽입
Subject Name: 조민석
```

### 3.3 Ticks 변환 (Windows DateTime.Ticks)

**구현:**
```python
def datetime_to_ticks(dt):
    base = datetime.datetime(1, 1, 1)
    delta = dt - base
    return int(delta.total_seconds() * 10_000_000)
```

**검증:**
- `datetime(1999, 11, 1)` → `630770112000000000` ✅
- 역변환 정확성 확인 (bidirectional) ✅

### 3.4 손잡이 매핑

**규칙:** ActiGraph는 주손의 **반대편** 손목에 착용

| Excel (주손) | 실제 손 | 장비 위치 | .agd/.gt3x Side | Dominance |
|-------------|---------|----------|----------------|-----------|
| **오** | 오른손잡이 | 왼쪽 손목 | **Left** | **Dominant** |
| **왼** | 왼손잡이 | 오른쪽 손목 | **Right** | **Non-Dominant** |

**구현:**
```python
def map_handedness(hand):
    mapping = {
        '오': ('Left', 'Dominant'),
        '왼': ('Right', 'Non-Dominant')
    }
    return mapping[hand]
```

---

## 4. 테스트 결과

### 4.1 테스트 환경

**대상자:** 조민석
**메타데이터:**
```python
{
    'subjectname': '조민석',
    'sex': 'Male',
    'height': 177,
    'mass': 70,
    'age': 26,
    'dateOfBirth': datetime(1999, 11, 1),
    'hand': '오',  # 오른손잡이
    'limb': 'Waist'
}
```

**테스트 파일:**
- Input: `Archive/original_MOS2A50130052 (2025-12-02)60sec.{agd,gt3x}`
- Reference: `Archive/modified_MOS2A50130052 (2025-12-02)60sec.{agd,gt3x}`
- Output: `temp_test/test.{agd,gt3x}`

### 4.2 테스트 1: .agd 파일 수정

**결과:** ✅ 성공

| 필드 | Test 값 | Reference 값 | 일치 |
|------|---------|-------------|------|
| subjectname | 조민석 | 조민석 | ✅ |
| sex | Male | Male | ✅ |
| height | 177 | 177 | ✅ |
| mass | 70 | 70 | ✅ |
| age | 26 | 26 | ✅ |
| dateOfBirth | 630770112000000000 | 630770112000000000 | ✅ |
| side | Left | Left | ✅ |
| dominance | Dominant | Dominant | ✅ |
| limb | Waist | Waist | ✅ |

**결론:** 9개 필드 모두 완벽히 일치

### 4.3 테스트 2: .gt3x 파일 수정

**결과:** ✅ 성공

| 필드 | Test 값 | Reference 값 | 일치 |
|------|---------|-------------|------|
| Subject Name | 조민석 | 조민석 | ✅ |
| Sex | Male | Male | ✅ |
| Height | 177 | 177 | ✅ |
| Mass | 70 | 70 | ✅ |
| Age | 26 | 26 | ✅ |
| DateOfBirth | 630770112000000000 | 630770112000000000 | ✅ |
| Side | Left | Left | ✅ |
| Dominance | Dominant | Dominant | ✅ |
| Limb | Waist | Waist | ✅ |

**결론:** 9개 필드 모두 완벽히 일치

### 4.4 테스트 3: 단위 테스트

**Ticks 변환:**
- ✅ datetime(1999, 11, 1) → 630770112000000000
- ✅ 역변환 정확 (bidirectional)

**손잡이 매핑:**
- ✅ "오" → (Left, Dominant)
- ✅ "왼" → (Right, Non-Dominant)

### 4.5 테스트 실행 방법

```bash
conda run -n module python modify.py --test
```

**출력:**
```
================================================================================
🎉 모든 테스트 통과!
================================================================================

✅ Progress 02 완료:
  - .agd 파일 수정 및 검증 성공
  - .gt3x 파일 수정 및 검증 성공
  - 모든 단위 테스트 통과
```

---

## 5. 사용 방법

### 5.1 테스트 모드 (Progress 02)

```bash
conda run -n module python modify.py --test
```

### 5.2 프로그래밍 방식 (Progress 04에서 사용 예정)

```python
from modify import ActiGraphModifier
import datetime

modifier = ActiGraphModifier("config.yaml")

metadata = {
    'subjectname': '조민석',
    'sex': 'Male',
    'height': 177,
    'mass': 70,
    'age': 26,
    'dateOfBirth': datetime.datetime(1999, 11, 1),
    'hand': '오'
}

# .agd 파일 수정
success = modifier.modify_agd_file("path/to/file.agd", metadata)

# .gt3x 파일 수정
success = modifier.modify_gt3x_file("path/to/file.gt3x", metadata)

# 검증
expected = {
    'subjectname': '조민석',
    'sex': 'Male',
    'height': 177,
    'mass': 70,
    'age': 26,
    'dateOfBirth': datetime.datetime(1999, 11, 1),
    'side': 'Left',
    'dominance': 'Dominant',
    'limb': 'Waist'
}

is_valid = modifier.validate_agd_modification("path/to/file.agd", expected)
is_valid = modifier.validate_gt3x_modification("path/to/file.gt3x", expected)
```

---

## 6. 핵심 발견 사항

### 6.1 .gt3x 파일의 필드 추가 필요

**문제:** Original 파일에는 Sex, Height, Mass, Age, DateOfBirth가 없음
**해결:** `_update_info_txt` 메서드에서 필드 삽입 로직 구현
- "Acceleration Max" 다음에 4개 필드 삽입
- "Dominance" 다음에 DateOfBirth 삽입

### 6.2 log.bin은 수정하지 않음

Progress 01에서 확인한 바와 같이, ActiLife는 주로 `info.txt`를 참조하므로 `log.bin`의 METADATA JSON은 수정하지 않아도 됩니다.

### 6.3 백업 및 복원 시스템

모든 수정 작업 전에 `.bak` 파일 생성하고, 실패 시 자동 복원하여 데이터 손실 방지

### 6.4 검증 로직

수정 후 9개 필드를 모두 검증하여 정확성 보장

---

## 7. 다음 단계 (Progress 03)

**목표:** Excel 데이터로 파일 수정하는 방법 계획 작성

**필요 작업:**
1. Excel 파일 (`대상자 키,체중,주손 정보.xlsx`) 구조 분석
2. 파일명과 Excel 데이터 매칭 방법 설계
3. name.py (파일명 변경) + modify.py (메타데이터 수정) 통합 워크플로우 설계
4. 일괄 처리 로직 계획

**참고 파일:**
- `Archive/대상자 키,체중,주손 정보.xlsx`
- `name.py` (파일명 변경 로직)
- `config.yaml` (경로 및 컬럼 매핑)

---

## 8. AI Agent 참고 사항

**Progress 02 폴더를 참고할 때:**

1. **modify.py 재사용:**
   - ActiGraphModifier 클래스를 import하여 사용
   - `modify_agd_file()`, `modify_gt3x_file()` 메서드 활용
   - metadata dict 형식 준수

2. **config.yaml 활용:**
   - metadata 섹션의 필드 매핑 사용
   - 손잡이 매핑 규칙 준수
   - 성별 매핑 활용

3. **검증 필수:**
   - 수정 후 항상 `validate_*_modification()` 호출
   - 9개 필드 모두 검증

4. **주의사항:**
   - .gt3x는 필드 삽입 위치 중요
   - log.bin은 수정하지 않음
   - 모든 값은 문자열로 저장
   - 백업 시스템 활용

**성공 기준:**
- ✅ modify.py 완전 구현
- ✅ config.yaml 업데이트
- ✅ 모든 단위 테스트 통과
- ✅ 통합 테스트: Test 파일이 Reference와 100% 일치
- ✅ 재사용 가능한 코드 (Progress 04 준비 완료)

**다음 작업:** Progress 03에서 Excel 데이터 연동 계획 수립
