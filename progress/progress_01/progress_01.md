# Progress 01: Meta Information 차이점 분석 완료

**작업 날짜**: 2025-12-03
**상태**: ✅ 완료
**목표**: Modified와 Original 파일 간의 meta information 차이점 찾기

---

## 1. 작업 개요

ActiGraph 가속도계 데이터 파일(.agd, .gt3x)의 메타데이터를 수정하기 위해, 먼저 ActiLife 프로그램에서 수동으로 수정한 파일과 원본 파일의 차이점을 분석했습니다.

**분석 대상 파일**:
- Modified: `Archive/modified_MOS2A50130052 (2025-12-02)60sec.agd` / `.gt3x`
- Original: `Archive/original_MOS2A50130052 (2025-12-02)60sec.agd` / `.gt3x`

---

## 2. 핵심 발견 사항

### 2.1 수정이 필요한 메타데이터 필드 (9개)

| 필드명 | 파일 형식 | 위치 | 예시 값 | 비고 |
|--------|----------|------|---------|------|
| **subjectname / Subject Name** | .agd / .gt3x | settings 테이블 / info.txt | 조민석 | 대상자별 |
| **sex / Sex** | .agd / .gt3x | settings 테이블 / info.txt | Male | 대상자별 |
| **height / Height** | .agd / .gt3x | settings 테이블 / info.txt | 177 | 대상자별 |
| **mass / Mass** | .agd / .gt3x | settings 테이블 / info.txt | 70 | 대상자별 |
| **age / Age** | .agd / .gt3x | settings 테이블 / info.txt | 26 | 대상자별 |
| **dateOfBirth / DateOfBirth** | .agd / .gt3x | settings 테이블 / info.txt | 630770112000000000 | 대상자별 |
| **side / Side** | .agd / .gt3x | settings 테이블 / info.txt | Left (오른손) / Right (왼손) | 손잡이별 ⚠️ |
| **dominance / Dominance** | .agd / .gt3x | settings 테이블 / info.txt | Dominant (오른손) / Non-Dominant (왼손) | 손잡이별 ⚠️ |
| **limb / Limb** | .agd / .gt3x | settings 테이블 / info.txt | Waist | 공통 (기본값) |

**⚠️ 중요**: 조민석이 오른손잡이라서 Modified와 Original이 모두 `Left + Dominant`로 동일했기 때문에 차이가 없었습니다. 하지만 왼손잡이의 경우 반드시 `Right + Non-Dominant`로 수정해야 합니다!

### 2.2 파일 구조 이해

#### .agd 파일 (SQLite Database)
```
.agd
├── settings 테이블 ← 메타데이터 저장 위치
├── data 테이블 (센서 데이터)
├── sleep, awakenings, filters 등
└── 기타 테이블들
```

**수정 방법**: Python `sqlite3` 라이브러리로 UPDATE 쿼리 실행

#### .gt3x 파일 (ZIP Archive)
```
.gt3x (ZIP)
├── info.txt ← 메타데이터 저장 위치 (텍스트)
├── log.bin (센서 데이터 + METADATA JSON)
└── calibration.json
```

**수정 방법**: ZIP 압축 해제 → info.txt 수정 → 재압축

### 2.3 중요한 발견: log.bin METADATA JSON

Modified 파일의 `info.txt`는 새 대상자 정보로 변경되었지만, `log.bin`의 METADATA JSON은 여전히 원래 정보(AB16_05)를 유지하고 있습니다.

```json
{
  "MetadataType": "Bio",
  "SubjectName": "AB16_05",  ← 수정되지 않음
  "Race": "Asian / Pacific Islander",
  "Limb": "Waist",
  "Side": "Left",
  "Dominance": "Dominant",
  "Parsed": false,
  "JSON": null
}
```

**결론**: ActiLife는 주로 `info.txt`를 참조하므로, METADATA JSON은 수정하지 않아도 되는 것으로 보입니다. (Progress 02에서 테스트 필요)

**참고**: METADATA JSON에도 Side, Dominance, Limb 필드가 있지만, SubjectName처럼 수정하지 않아도 작동하는지는 추가 검증이 필요합니다.

---

## 3. 데이터 형식 규칙

### 3.1 Ticks 형식 (Windows DateTime.Ticks)

- **기준점**: 0001-01-01 00:00:00
- **1 Tick** = 100 nanoseconds = 10^-7 seconds
- **예시**: `630770112000000000` = 1999-11-01 ✓ 검증완료

```python
import datetime

def datetime_to_ticks(dt):
    base = datetime.datetime(1, 1, 1)
    delta = dt - base
    return int(delta.total_seconds() * 10_000_000)

def ticks_to_datetime(ticks):
    base = datetime.datetime(1, 1, 1)
    return base + datetime.timedelta(microseconds=int(ticks) / 10)
```

### 3.2 손잡이 매핑 규칙 ⚠️ 중요

**규칙**: ActiGraph 장비는 주손의 **반대편** 손목에 착용합니다.

| Excel (주손) | .agd/.gt3x (Side) | .agd/.gt3x (Dominance) | 착용 위치 |
|-------------|-------------------|----------------------|-----------|
| **오** (오른손잡이) | **Left** | **Dominant** | 왼쪽 손목 |
| **왼** (왼손잡이) | **Right** | **Non-Dominant** | 오른쪽 손목 |

**이유**:
- 오른손잡이 → 오른손 주로 사용 → 왼쪽 손목이 안정적 → Left + Dominant
- 왼손잡이 → 왼손 주로 사용 → 오른쪽 손목이 안정적 → Right + Non-Dominant

---

## 4. 분석 결과 상세

### 4.1 .agd 파일 차이점 (11개)

| 필드명 | Modified | Original | 비고 |
|--------|----------|----------|------|
| subjectname | 조민석 | AB16_05 | ✅ 핵심 |
| sex | Male | Undefined | ✅ 핵심 |
| height | 177 | 0 | ✅ 핵심 |
| mass | 70 | 0 | ✅ 핵심 |
| age | 26 | 0 | ✅ 핵심 |
| dateOfBirth | 630770112000000000 | 0 | ✅ 핵심 |
| batteryvoltage | 4.18 | 4.17 | 자동 변경 |
| downloaddatetime | 639003130690000000 | 639003126230000000 | 자동 변경 |
| stopdatetime | 639003130690000000 | 639003126230000000 | 자동 변경 |
| epochcount | 33057 | 33050 | 자동 변경 |
| sleepscorealgorithmname | (empty) | Cole-Kripke | 자동 변경 |

### 4.2 .gt3x 파일 차이점 (9개)

**info.txt 차이점**:
| 필드명 | Modified | Original | 비고 |
|--------|----------|----------|------|
| Subject Name | 조민석 | AB16_05 | ✅ 핵심 |
| Sex | Male | (없음) | ✅ 핵심 |
| Height | 177 | (없음) | ✅ 핵심 |
| Mass | 70 | (없음) | ✅ 핵심 |
| Age | 26 | (없음) | ✅ 핵심 |
| DateOfBirth | 630770112000000000 | (없음) | ✅ 핵심 |
| Battery Voltage | 4.18 | 4.17 | 자동 변경 |
| Download Date | 639003130690000000 | 639003126230000000 | 자동 변경 |
| Last Sample Time | 639003130690000000 | 639003126230000000 | 자동 변경 |

**log.bin METADATA JSON**: 차이 없음 (수정 불필요)

---

## 5. 생성된 파일 목록

### 분석 스크립트
1. **analyze_agd.py**: .agd 파일 분석 및 비교
2. **analyze_gt3x.py**: .gt3x 파일 분석 및 비교
3. **verify_dateofbirth.py**: Ticks 변환 검증

### 결과 파일
1. **agd_differences.json**: .agd 차이점 JSON
2. **gt3x_differences.json**: .gt3x 차이점 JSON
3. **METADATA_DIFFERENCES_REPORT.md**: 상세 분석 보고서

---

## 6. 다음 단계 (Progress 02)

**목표**: Original 파일을 파이썬으로 수정해 Modified와 동일하게 만들기

**필요 작업**:
1. .agd 파일 수정 함수 작성
2. .gt3x 파일 수정 함수 작성
3. 테스트 실행 및 검증
4. 사용자 컨펌

**필요 입력 데이터** (예시):
```python
metadata = {
    'subjectname': '조민석',
    'sex': 'Male',
    'height': 177,
    'mass': 70,
    'age': 26,
    'dateOfBirth': datetime.datetime(1999, 11, 1),
    'side': 'Left',          # 오른손잡이: Left, 왼손잡이: Right
    'dominance': 'Dominant', # 오른손잡이: Dominant, 왼손잡이: Non-Dominant
    'limb': 'Waist'          # 기본값
}
```

---

## 7. AI Agent 참고 사항

이 폴더(`progress/progress_01/`)를 참고할 때:

1. **메타데이터 필드 확인**: **9개 필드** 수정 필요
   - 대상자별 (6개): subjectname, sex, height, mass, age, dateOfBirth
   - 손잡이별 (2개): side, dominance ⚠️ 중요!
   - 공통 (1개): limb

2. **파일 구조 이해**:
   - .agd = SQLite (settings 테이블에 9개 필드 모두 있음)
   - .gt3x = ZIP (info.txt에 9개 필드 모두 있음)

3. **손잡이 매핑 규칙** ⚠️ 필수:
   - 오른손잡이: Side=**Left**, Dominance=**Dominant**
   - 왼손잡이: Side=**Right**, Dominance=**Non-Dominant**
   - 주손의 **반대편** 손목에 착용하기 때문!

4. **Ticks 변환**: 생년월일은 Ticks 형식으로 변환 필요

5. **METADATA JSON**: 수정 불필요로 보임 (info.txt만 변경, Progress 02에서 검증 필요)

**핵심 원칙**: ActiLife 프로그램의 수정 방식을 파이썬으로 재현하는 것이 목표입니다.

**⚠️ 주의**: 조민석 샘플은 오른손잡이라서 side/dominance 차이가 없었습니다. 왼손잡이 케이스를 반드시 고려해야 합니다!
