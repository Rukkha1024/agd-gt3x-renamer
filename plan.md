<purpose> 
사용자는 accelermometer 장비의 데이터를 추출 시, actilife 프로그램 내에서 meta information을 수정하지 않고 .agd, .gt3x 파일의 정보를 파이썬으로 직접 수정하고자 한다. 
</purpose>

<request>
do progress number 2. 
</request>

<rule>
- 현 codebase rule을 준수해라. 
- 파이썬 코드를 만든다면, @name.py을 포함해서, 3개 이하로 만들어라. 
</rule>

<working progress>
1. meta information이 다른점을 찾기 between <modified> and <original>
2. 다른점을 찾은 후, <original> 파일을 파이썬으로 수정해 <modified>와 동일하게 만들기. # 동일하게 만들어졌는지 사용자의 컨펌이 필요. 
3. 동일하게 만들어졌다면, "Archive/대상자 키,체중,주손 정보.xlsx" 파일을 통해서 외부데이터의 정보를 통해서 <original> 파일들을 <modified>로 바꾸는 방법에 대해서 계획 작성. "Archive/대상자 키,체중,주손 정보.xlsx" 파일을 통해서 .agd, .gt3x 파일과 어떻게 매칭할 수 있는지는 <file rename> 참조할 것. 
4. 3의 계획을 파이썬코드로 작성. 
5. <original> 파일에 대해서 만들어둔 파이썬 script로 <file rename>과 meta information까지 수정. 
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
