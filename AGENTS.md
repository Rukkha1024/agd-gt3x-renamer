## Work Procedure
Always follow this procedure when performing tasks:
1. **Plan the changes**: Before making any code modifications, create a detailed plan outlining what will be changed and why
2. **Get user confirmation**: Present the plan to the user and wait for explicit confirmation before proceeding
3. **Modify code**: Make the necessary code changes according to the confirmed plan
4. **Git commit in Korean**: Commit your changes with a Korean commit message
5. **Run the modified code**: Execute the modified code to verify your work

---
## Environment rules
- Use the existing conda env: `cuda` (WSL2).
- Always run Python/pip as: `conda run -n cuda python` / `conda run -n cuda pip`.
- **Do not** create or activate any `venv` or `.venv` or run `uv venv`.
- If a package is missing, prefer:
  1) `mamba/conda install -n cuda <pkg>` (if available)
  2) otherwise `conda run -n cuda pip install <pkg>`
- Before running Python, verify the interpreter path with:
  `conda run -n cuda python -c "import sys; print(sys.executable)"`

--
## Code Rules 
- Always design code for high reusability and central control via `config.yaml`.
- Whenever you see the same logic or configuration emerge in two or more places, refactor it into a `config.yaml` entry for the parameters.
- Before introducing a new constant or parameter in code, first ask: “Should this live in `config.yaml` so it can be centrally managed?” If yes, add it to `config.yaml` and reference it from there.
