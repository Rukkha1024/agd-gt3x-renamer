# Meta Information Differences Report

## Progress 1 완료: Modified vs Original 파일 간 차이점 분석

분석 날짜: 2025-12-03
분석 대상:
- Modified: `modified_MOS2A50130052 (2025-12-02)60sec.agd` / `.gt3x`
- Original: `original_MOS2A50130052 (2025-12-02)60sec.agd` / `.gt3x`

---

## 1. .agd 파일 차이점 (SQLite Database)

### 차이점 요약
`.agd` 파일의 **`settings` 테이블**에서 총 **11개 필드**의 차이점이 발견되었습니다.

### 상세 차이점

| 필드명 | Modified 값 | Original 값 | 설명 |
|--------|-------------|-------------|------|
| **subjectname** | 조민석 | AB16_05 | 대상자 이름 |
| **sex** | Male | Undefined | 성별 |
| **height** | 177 | 0 | 키 (cm) |
| **mass** | 70 | 0 | 체중 (kg) |
| **age** | 26 | 0 | 나이 |
| **dateOfBirth** | 630770112000000000 | 0 | 생년월일 (Ticks) |
| batteryvoltage | 4.18 | 4.17 | 배터리 전압 |
| downloaddatetime | 639003130690000000 | 639003126230000000 | 다운로드 시간 (Ticks) |
| stopdatetime | 639003130690000000 | 639003126230000000 | 측정 종료 시간 (Ticks) |
| epochcount | 33057 | 33050 | Epoch 개수 |
| sleepscorealgorithmname | (empty) | Cole-Kripke | 수면 점수 알고리즘 |

### 수정이 필요한 핵심 필드 (굵은 글씨)
1. **subjectname**: 대상자 이름
2. **sex**: 성별
3. **height**: 키
4. **mass**: 체중
5. **age**: 나이
6. **dateOfBirth**: 생년월일

---

## 2. .gt3x 파일 차이점 (Zip Archive)

### 파일 구조
```
.gt3x (ZIP)
├── info.txt          # 장치 정보 및 메타데이터 (텍스트)
├── log.bin           # 센서 데이터 및 METADATA 패킷 (바이너리)
└── calibration.json  # 캘리브레이션 정보
```

### 2.1 info.txt 차이점
총 **9개 필드**에서 차이점이 발견되었습니다.

| 필드명 | Modified 값 | Original 값 | 설명 |
|--------|-------------|-------------|------|
| **Subject Name** | 조민석 | AB16_05 | 대상자 이름 |
| **Sex** | Male | (없음) | 성별 |
| **Height** | 177 | (없음) | 키 (cm) |
| **Mass** | 70 | (없음) | 체중 (kg) |
| **Age** | 26 | (없음) | 나이 |
| **DateOfBirth** | 630770112000000000 | (없음) | 생년월일 (Ticks) |
| Battery Voltage | 4.18 | 4.17 | 배터리 전압 |
| Download Date | 639003130690000000 | 639003126230000000 | 다운로드 날짜 (Ticks) |
| Last Sample Time | 639003130690000000 | 639003126230000000 | 마지막 샘플 시간 (Ticks) |

### 수정이 필요한 핵심 필드 (굵은 글씨)
1. **Subject Name**: 대상자 이름
2. **Sex**: 성별
3. **Height**: 키
4. **Mass**: 체중
5. **Age**: 나이
6. **DateOfBirth**: 생년월일

### 2.2 log.bin METADATA JSON 차이점
**차이점 없음** - 두 파일 모두 동일한 METADATA JSON을 가지고 있습니다.

```json
{
  "MetadataType": "Bio",
  "SubjectName": "AB16_05",
  "Race": "Asian / Pacific Islander",
  "Limb": "Waist",
  "Side": "Left",
  "Dominance": "Dominant",
  "Parsed": false,
  "JSON": null
}
```

**중요 발견**: Modified 파일의 `info.txt`에는 새 대상자 정보(조민석)가 반영되었지만, `log.bin`의 METADATA JSON에는 여전히 원래 정보(AB16_05)가 남아있습니다.

---

## 3. 수정 전략 요약

### 3.1 .agd 파일 수정 방법
- **파일 형식**: SQLite Database
- **수정 대상**: `settings` 테이블
- **수정 필드**:
  - subjectname
  - sex
  - height
  - mass
  - age
  - dateOfBirth

**수정 방법**: Python `sqlite3` 라이브러리로 UPDATE 쿼리 실행

```python
import sqlite3

conn = sqlite3.connect('file.agd')
cursor = conn.cursor()

# 예시
cursor.execute("UPDATE settings SET settingValue=? WHERE settingName='subjectname'", ('조민석',))
cursor.execute("UPDATE settings SET settingValue=? WHERE settingName='sex'", ('Male',))
cursor.execute("UPDATE settings SET settingValue=? WHERE settingName='height'", ('177',))
cursor.execute("UPDATE settings SET settingValue=? WHERE settingName='mass'", ('70',))
cursor.execute("UPDATE settings SET settingValue=? WHERE settingName='age'", ('26',))
cursor.execute("UPDATE settings SET settingValue=? WHERE settingName='dateOfBirth'", ('630770112000000000',))

conn.commit()
conn.close()
```

### 3.2 .gt3x 파일 수정 방법
- **파일 형식**: ZIP Archive
- **수정 대상**: `info.txt` (텍스트 파일)
- **수정 필드**: .agd와 동일

**수정 방법**:
1. ZIP 압축 해제
2. `info.txt` 텍스트 수정 (Key: Value 형식)
3. 다시 ZIP으로 압축

```python
import zipfile

# 1. 압축 해제 및 읽기
with zipfile.ZipFile('original.gt3x', 'r') as zf:
    info_data = zf.read('info.txt').decode('utf-8')
    log_bin = zf.read('log.bin')
    calibration = zf.read('calibration.json')

# 2. info.txt 수정
new_lines = []
for line in info_data.split('\n'):
    if line.startswith('Subject Name:'):
        new_lines.append('Subject Name: 조민석')
    elif line.startswith('Sex:'):
        new_lines.append('Sex: Male')
    # ... 나머지 필드 수정
    else:
        new_lines.append(line)

new_info = '\n'.join(new_lines)

# 3. 새 .gt3x 파일 생성
with zipfile.ZipFile('modified.gt3x', 'w') as zf:
    zf.writestr('info.txt', new_info.encode('utf-8'))
    zf.writestr('log.bin', log_bin)
    zf.writestr('calibration.json', calibration)
```

### 3.3 log.bin METADATA JSON 수정 여부
- **현재 상태**: Modified 파일도 METADATA JSON은 수정되지 않았음
- **권장 사항**: info.txt 수정만으로 충분해 보임
- **이유**:
  - ActiLife 프로그램이 주로 info.txt를 참조하는 것으로 보임
  - METADATA JSON 수정은 복잡하고 위험성이 높음 (패킷 크기, 체크섬 재계산 필요)

---

## 4. 다음 단계 (Progress 2)

Progress 1 완료되었습니다. 다음은 Progress 2를 진행해야 합니다:

**Progress 2 목표**: Original 파일을 파이썬으로 수정해 Modified와 동일하게 만들기

### 작업 내용
1. `.agd` 파일 수정 함수 작성
2. `.gt3x` 파일 수정 함수 작성
3. 테스트 실행: Original 파일 복사 → 수정 → Modified 파일과 비교
4. 사용자 컨펌: 동일하게 만들어졌는지 확인

### 필요한 입력 데이터
- 대상자 이름 (subjectname / Subject Name)
- 성별 (sex / Sex)
- 키 (height / Height)
- 체중 (mass / Mass)
- 나이 (age / Age)
- 생년월일 (dateOfBirth / DateOfBirth) - Ticks 형식

---

## 부록 A: Ticks 형식 변환

ActiGraph는 Windows DateTime.Ticks 형식을 사용합니다.
- 1 Tick = 100 nanoseconds = 10^-7 seconds
- 기준점: 0001-01-01 00:00:00

### Python 변환 함수

```python
import datetime

def datetime_to_ticks(dt):
    """datetime을 Ticks로 변환"""
    base = datetime.datetime(1, 1, 1)
    delta = dt - base
    ticks = int(delta.total_seconds() * 10_000_000)
    return ticks

def ticks_to_datetime(ticks):
    """Ticks를 datetime으로 변환"""
    base = datetime.datetime(1, 1, 1)
    dt = base + datetime.timedelta(microseconds=int(ticks) / 10)
    return dt

# 예시: Modified 파일의 생년월일
ticks_value = 630770112000000000
converted_date = ticks_to_datetime(ticks_value)
print(f"Ticks: {ticks_value}")
print(f"생년월일: {converted_date}")
# 결과: 1999-11-01 00:00:00 ✓ 검증 완료
```

## 부록 B: 손잡이(주손) 매핑 규칙

**중요**: ActiGraph 장비는 주손의 **반대편** 손목에 착용합니다.

### 매핑 규칙

| Excel (주손) | .agd / .gt3x (Side) | .agd / .gt3x (Dominance) | 설명 |
|-------------|---------------------|-------------------------|------|
| **오** (오른손잡이) | **Left** | **Dominant** | 왼쪽 손목에 착용 |
| **왼** (왼손잡이) | **Right** | **Non-Dominant** | 오른쪽 손목에 착용 |

### 이유
- 오른손잡이는 오른손을 주로 사용 → 왼쪽 손목이 더 안정적 → Left + Dominant
- 왼손잡이는 왼손을 주로 사용 → 오른쪽 손목이 더 안정적 → Right + Non-Dominant

### Python 구현 (config.yaml에 저장됨)

```python
dominant_hand_mapping = {
    '오': {
        'side': 'Left',
        'dominance': 'Dominant'
    },
    '왼': {
        'side': 'Right',
        'dominance': 'Non-Dominant'
    }
}
```

---

## 분석 파일 위치
- AGD 차이점: `Archive/agd_differences.json`
- GT3X 차이점: `Archive/gt3x_differences.json`
- 분석 스크립트:
  - `analyze_agd.py`
  - `analyze_gt3x.py`
