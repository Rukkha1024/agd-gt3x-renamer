# 추가 발견: 손잡이 관련 필드 (Side, Dominance, Limb)

**날짜**: 2025-12-03
**업데이트**: Progress 01에 추가 분석 수행

---

## 발견 경위

초기 분석에서 Modified와 Original 파일의 차이점이 **6개 필드**로 확인되었습니다. 하지만 사용자 지적에 따라 **손잡이(주손) 정보**도 수정해야 할 필드임을 확인했습니다.

**왜 차이가 없었나?**
- 조민석 샘플이 **오른손잡이**였기 때문
- Modified와 Original 모두 `Side: Left, Dominance: Dominant`로 동일
- 따라서 초기 비교 분석에서 차이가 감지되지 않음

---

## 확인된 필드

### .agd 파일 (settings 테이블)
```sql
side: Left
dominance: Dominant
limb: Waist
```

### .gt3x 파일 (info.txt)
```
Side: Left
Dominance: Dominant
Limb: Waist
```

### .gt3x 파일 (METADATA JSON)
```json
{
  "Side": "Left",
  "Dominance": "Dominant",
  "Limb": "Waist"
}
```

---

## 손잡이 매핑 규칙

**핵심 원리**: ActiGraph 장비는 주손의 **반대편** 손목에 착용합니다.

| Excel (주손 컬럼) | 착용 위치 | .agd/.gt3x (Side) | .agd/.gt3x (Dominance) |
|------------------|----------|-------------------|----------------------|
| **오** (오른손잡이) | 왼쪽 손목 | **Left** | **Dominant** |
| **왼** (왼손잡이) | 오른쪽 손목 | **Right** | **Non-Dominant** |

### 이유
- **오른손잡이**: 오른손을 주로 사용 → 왼쪽 손목이 더 안정적 → Left 착용 + Dominant
- **왼손잡이**: 왼손을 주로 사용 → 오른쪽 손목이 더 안정적 → Right 착용 + Non-Dominant

---

## 수정이 필요한 전체 필드 (최종)

총 **9개 필드**:

### 대상자 개인 정보 (6개)
1. subjectname / Subject Name
2. sex / Sex
3. height / Height
4. mass / Mass
5. age / Age
6. dateOfBirth / DateOfBirth

### 손잡이 정보 (2개) ⚠️
7. **side / Side**
8. **dominance / Dominance**

### 공통 정보 (1개)
9. limb / Limb (기본값: Waist)

---

## Progress 02에서 확인 필요 사항

1. **.gt3x METADATA JSON 수정 여부**:
   - info.txt만 수정해도 되는지
   - METADATA JSON도 수정해야 하는지
   - SubjectName은 METADATA JSON에서 수정 안 했는데도 작동했음
   - Side, Dominance도 동일하게 작동하는지 검증 필요

2. **왼손잡이 테스트 케이스**:
   - 왼손잡이 대상자로 수정 테스트 필요
   - Side: Right, Dominance: Non-Dominant 정상 작동 확인

---

## 분석에 사용된 스크립트

**check_dominance_fields.py**: Side, Dominance, Limb 필드 확인 스크립트

```python
# 주요 로직
- .agd: settings 테이블에서 side, dominance, limb 검색
- .gt3x: info.txt에서 Side, Dominance, Limb 추출
- .gt3x: METADATA JSON에서 Side, Dominance, Limb 파싱
```

---

## 결론

**Progress 01 최종 수정 사항**:
- 수정 필요 필드: 6개 → **9개**
- 손잡이 정보(side, dominance)는 왼손잡이 케이스에서 반드시 수정 필요
- Limb는 기본값(Waist) 사용
- progress_01.md 업데이트 완료
