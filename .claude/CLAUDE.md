## Progress 작업 기록 참고 (최우선)
**이 프로젝트는 5단계 working progress로 진행됩니다. 작업 시 반드시 progress 폴더를 참고하세요.**

### 필수 규칙
1. **작업 시작 전**: 반드시 `.claude/PROGRESS_GUIDE.md`와 해당 `progress/progress_XX/` 폴더를 읽고 이해하세요
2. **이전 작업 참고**: 현재 progress 뿐만 아니라 이전 모든 progress 폴더의 내용을 참고하세요
3. **작업 기록**: 작업 완료 후 새로운 `progress/progress_XX/` 폴더에 결과를 기록하세요

### Progress 폴더 구조
```
progress/
├── progress_01/  ✅ Meta Information 차이점 분석 (완료)
├── progress_02/  ⏳ Original 파일 수정 및 검증 (대기)
├── progress_03/  ⏳ 외부 데이터 연동 계획 (대기)
├── progress_04/  ⏳ 자동화 스크립트 작성 (대기)
└── progress_05/  ⏳ 최종 실행 및 검증 (대기)
```

### 핵심 참고 파일
- `.claude/PROGRESS_GUIDE.md`: Progress 전체 가이드
- `progress/progress_01/progress_01.md`: 메타데이터 차이점 분석 결과
- 각 progress의 `progress_XX.md`: 해당 작업 요약

---

## Work Procedure
Always follow this procedure when performing tasks:
1. **Check progress folder**: 작업 시작 전 관련 progress 폴더 확인 (필수)
2. **Plan the changes**: Before making any code modifications, create a detailed plan outlining what will be changed and why
3. **Get user confirmation**: Present the plan to the user and wait for explicit confirmation before proceeding
4. **Modify code**: Make the necessary code changes according to the confirmed plan
5. **Git commit in Korean**: Commit your changes with a Korean commit message
6. **Run the modified code**: Execute the modified code to verify your work
7. **Record in progress folder**: 작업 결과를 해당 progress 폴더에 기록

---
## Environment rules
- Use the existing conda env: `module` (WSL2).
- Always run Python/pip as: `conda run -n module python` / `conda run -n module pip`.
- **Do not** create or activate any `venv` or `.venv` or run `uv venv`.
- If a package is missing, prefer:
  1) `mamba/conda install -n module <pkg>` (if available)
  2) otherwise `conda run -n module pip install <pkg>`
- Before running Python, verify the interpreter path with:
  `conda run -n module python -c "import sys; print(sys.executable)"`

--
## Code Rules 
- Always design code for high reusability and central control via `config.yaml`.
- Whenever you see the same logic or configuration emerge in two or more places, refactor it into a `config.yaml` entry for the parameters.
- Before introducing a new constant or parameter in code, first ask: “Should this live in `config.yaml` so it can be centrally managed?” If yes, add it to `config.yaml` and reference it from there.
- when you handling `.agd`, `.gt3x` format file, read @Archive\.agd 수정 예시.md, @Archive\.gt3x 수정 예시.md, @Archive\agd, .gt3x 파일 수정 시 참고할 사항.md.