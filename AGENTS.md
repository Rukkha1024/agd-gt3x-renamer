## Work Procedure
Always follow this procedure when performing tasks:
1. **Plan the changes**: Before making any code modifications, create a detailed plan outlining what will be changed and why
2. **Get user confirmation**: Present the plan to the user and wait for explicit confirmation before proceeding
3. **Modify code**: Make the necessary code changes according to the confirmed plan
4. **Git commit in Korean**: Commit your changes with a Korean commit message
5. **Run the modified code**: Execute the modified code to verify your work

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
- when you handling `.agd`, `.gt3x` format file, read @.agd 수정 예시.md, @.gtx3 수정 예시.md, @agd, .gt3x 파일 수정 시 참고할 사항.md. 
