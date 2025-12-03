<purpose> 
사용자는 accelermometer 장비의 데이터를 추출 시, actilife 프로그램 내에서 meta information을 수정하지 않고 .agd, .gt3x 파일의 정보를 파이썬으로 직접 수정하고자 한다. 
</purpose>

<request>
Progress 05 구현
</request>

<rule>
- 현 codebase rule을 준수해라. 
- 파이썬 코드를 만든다면, @name.py을 포함해서, 3개 이하로 만들어라. 
</rule>

<working progress>
1. meta information이 다른점을 찾기 between <modified> and <original> 
2. 다른점을 찾은 후, <original> 파일을 파이썬으로 수정해 <modified>와 동일하게 만들기 
3. Excel 데이터를 통해 파일을 수정하는 방법에 대한 계획 작성 
   - Excel 데이터 매칭 전략 설계 완료
   - 메타데이터 변환 규칙 정의 완료
   - name.py + modify.py 통합 워크플로우 설계 완료
   - 상세 계획: progress/progress_03/progress_03.md
4. 3의 계획을 파이썬코드로 작성 
   - name.py에 메타데이터 추출 및 수정 기능 통합 완료
   - config.yaml에 메타데이터 컬럼 매핑 추가 완료
   - 테스트 성공: 메타데이터 + 파일명 일괄 변경 검증 완료
   - 상세 결과: progress/progress_04/progress_04.md
5. <original> 파일에 대해서 만들어둔 파이썬 script로 <file rename>과 meta information까지 수정 
   - Original 파일 처리 성공: 파일명 변경 + 메타데이터 수정 완료
   - Excel 병합 셀 처리 버그 수정 (name.py)
   - 9개 메타데이터 필드 검증 성공 (.agd, .gt3x)
   - 실제 사용 가능한 최종 결과물 완성
   - 상세 결과: progress/progress_05/progress_05.md
</working progress>

<기타 참고 사항>
오른손잡이: 
 - 엑셀: 주손 == '오' 
 - .agd, .gt3x: side == 'Left' & Dominance =="Dominant"
	
왼손잡이: 
 - 엑셀: 주손 == '왼'
 - .agd, .gt3x: side == 'Right' & Dominance =="Non-Dominant"
</기타 참고 사항>


<file rename>
- name.py
- config.yaml 
</file rename>


<reference file>
<modified>
Archive/modified_MOS2A50130052 (2025-12-02)60sec.agd
Archive/modified_MOS2A50130052 (2025-12-02)60sec.gt3x
</modified>
<original>
Archive/original_MOS2A50130052 (2025-12-02)60sec.gt3x
Archive/original_MOS2A50130052 (2025-12-02)60sec.agd
</original>
/reference file>
