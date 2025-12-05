# References and Considerations for Modifying .agd and .gt3x Files

## 1. Documents and Packages Referenced for `.agd` Files

### (1) ActiLife User's Manual – AGD = SQLite Structure

1.  **ActiLife 5 User’s Manual (PDF)**
    *   **Content:**
        *   States that for devices other than GT3X+, data is saved in `*.agd` format upon download, and this format is **compatible with SQLite databases**.
        *   Explains that the `*.agd` file schema is included in Appendix A of the manual. ([dl.theactigraph.com](https://dl.theactigraph.com/ActiLife5-PUB10DOC10-F.pdf?utm_source=chatgpt.com "ActiLife 5 -User's Manual"))
    *   **Purpose of Use:**
        *   Establishing the premise that "AGD = SQLite DB".
        *   Confirming what table structure to expect (noting the schema is in the appendix).

2.  **ActiLife Documentation / ActiLife 6 User’s Manual (PDF)**
    *   **Example:** `ActiLife Documentation, Release 0.0.1`
    *   **Content:**
        *   Explains that ActiLife generates **native `*.agd` files** during the download/export process and that these files are **SQLite format (small databases)**. ([media.readthedocs.org](https://media.readthedocs.org/pdf/actilife/latest/actilife.pdf?utm_source=chatgpt.com "ActiLife Documentation"))
    *   **Purpose of Use:**
        *   Reconfirming that AGD is SQLite format in the latest versions as well.
        *   Provides confidence that opening it with `sqlite3` in code is the standard approach.

3.  **ActiLifeManual GitHub Repository – Appendix A Reference**
    *   **Repository:** `actigraph/ActiLifeManual` ([GitHub](https://github.com/actigraph/ActiLifeManual?utm_source=chatgpt.com "actigraph/ActiLifeManual: Manual for ActiLife 6"))
    *   In documents like `devices.rst`, there is a statement: "Please refer to ActiLife Appendix A – File Types for the `*.agd` schema." ([GitHub](https://github.com/actigraph/ActiLifeManual/blob/main/docs/devices.rst?utm_source=chatgpt.com "ActiLifeManual/docs/devices.rst at main · actigraph ..."))
    *   **Purpose of Use:**
        *   Reconfirming that Appendix A is the "canonical" source for the AGD schema.
        *   Basis for judgment that SQLite table names/columns must align with Appendix A.

### (2) R Package Documentation Handling AGD

4.  **`activAnalyzer` / `actigraph.sleepr` Packages – `read_agd_raw` Documentation**
    *   **`read_agd_raw` Description Page:**
        *   Explicitly states, "AGD files are SQLite DBs and contain at least 5 tables: `data`, `sleep`, `filters`, `settings`, `awakenings`." ([rdrr.io](https://rdrr.io/github/dipetkov/actigraph.sleepr/man/read_agd_raw.html?utm_source=chatgpt.com "read_agd_raw: Read an *.agd file, with no post-processing"))
        *   Notes that the table schema follows Appendix A of the ActiLife 6 User’s Manual. ([GitHub](https://github.com/dipetkov/actigraph.sleepr/blob/master/R/read_agd.R?utm_source=chatgpt.com "actigraph.sleepr/R/read_agd.R at master · dipetkov ..."))
    *   **Purpose of Use:**
        *   Understanding the actual internal table names and basic column composition of AGD files.
        *   Clarifying which tables to expect when opening with `sqlite3` in Python.
        *   For future coding:
            *   Assumes `settings` is for subject info modification.
            *   Assumes `data` table is for time series data.

5.  **Other Reference: Actinfo Thesis (ActiLife Data Format Explanation)**
    *   **From "Information Platform for Physical Activity" Master's Thesis:**
        *   Explains that `*.gt3x` is a **binary, proprietary format**, and
        *   After converting `*.gt3x → *.agd` via ActiLife, the `*.agd` is much more accessible. ([fenix.tecnico.ulisboa.pt](https://fenix.tecnico.ulisboa.pt/downloadFile/563345090417283/Dissertation__Information_Platform_for_Physical_Activity.pdf?utm_source=chatgpt.com "Actinfo: Information Platform for Physical Activity - Fenix"))
    *   **Purpose of Use:**
        *   Reconfirming practically that "dealing with `.agd` directly is much better than raw `.gt3x`."
        *   Justification for the research workflow strategy of opening `.agd` with SQLite rather than touching `.gt3x` directly.

---

## 2. Documents and Packages Referenced for `.gt3x` Files

### (1) Official File Format Documentation (ActiGraph GitHub)

1.  **`actigraph/GT3X-File-Format` GitHub Repository (Latest Format)**
    *   **README:**
        *   Explains that `.gt3x` files are **zip archives** containing `log.bin` (log records), `info.txt` (device info and start/download times), etc. ([GitHub](https://github.com/actigraph/GT3X-File-Format?utm_source=chatgpt.com "Documentation of the ActiGraph .gt3x file format"))
    *   **`LogRecords/Metadata.md` (Raw Version):**
        *   **METADATA Packet – ID 6** documentation.
        *   States that "Arbitrary metadata content" is stored as a JSON string.
        *   Example JSON includes: `{"MetadataType":"Bio","SubjectName":"...","Race":"","Limb":"","Side":"","Dominance":"","Parsed":false,"JSON":null}`. ([GitHub](https://raw.githubusercontent.com/actigraph/GT3X-File-Format/main/LogRecords/Metadata.md "raw.githubusercontent.com"))
        *   Explains the header (separator 0x1E, type 0x06, timestamp, size field), payload, and checksum calculation location.
    *   **Purpose of Use:**
        *   Understanding the `.gt3x` structure as **zip → info.txt + log.bin**.
        *   Identifying the location/format where metadata is stored as JSON (UTF-8) inside `log.bin`.
        *   Basis for designing the "modify METADATA Bio packet → recalculate size/checksum" process.

2.  **`actigraph/NHANES-GT3X-File-Format` GitHub Repository (Old Format)**
    *   **"File Format" Section in README:**
        *   States that `.gt3x` is a zip, and the file list includes:
            *   `info.txt` – Device information including start date and download date.
            *   `metadata` – Subject Biometric Data. ([GitHub](https://github.com/actigraph/NHANES-GT3X-File-Format?utm_source=chatgpt.com "actigraph/NHANES-GT3X-File-Format"))
    *   **Purpose of Use:**
        *   Reconfirming the structure where `info.txt` holds device/basic info, while `metadata` holds **Subject Biometric Data**.
        *   Although it's the old NHANES format, it is referenced because of the continuity in design philosophy with the latest GT3X-File-Format.

### (2) R Packages Reading GT3X – Structure and Metadata Examples

3.  **R Package `read.gt3x` – README and Reference Manual**
    *   **README:**
        *   Explains that the `.gt3x` file is a **zipped directory containing `log.bin` and `info.txt`**. ([CRAN](https://cran.r-project.org/web/packages/read.gt3x/readme/README.html?utm_source=chatgpt.com "read.gt3x"))
        *   Specifies that `info.txt` is a simple text file containing device-related meta information. ([CRAN](https://cran.r-project.org/web/packages/read.gt3x/readme/README.html?utm_source=chatgpt.com "read.gt3x"))
    *   **Function `parse_gt3x_info` Documentation:**
        *   Input is a `.gt3x` file; it extracts metadata by parsing the internal `info.txt`.
        *   `extract_gt3x_info` takes the `info.txt` file path itself as input. ([rdrr.io](https://rdrr.io/cran/read.gt3x/man/parse_gt3x_info.html?utm_source=chatgpt.com "parse_gt3x_info: Parse GT3X info.txt file"))
    *   **Purpose of Use:**
        *   Confirming the practice of "practically unzip → read info.txt → process header metadata."
        *   Evidence that we can follow a similar approach (unzip and parse `info.txt`) in Python.

4.  **R Package `SummarizedActigraphy` – Vignette _Summarizing Actigraphy Data_**
    *   In the example code, printing `x$header` after reading a `.gt3x` file shows fields such as:
        *   Serial Number, Device Type, Firmware, Battery Voltage, Sample Rate, Start/Stop/Download Date, Sex, Height, Mass, Age, Race, Limb, Side, Dominance, DateOfBirth, Subject Name, etc. ([johnmuschelli.com](https://johnmuschelli.com/SummarizedActigraphy/articles/Summarizing_Actigraphy_Data.html?utm_source=chatgpt.com "Summarizing Actigraphy Data - John Muschelli"))
    *   **Purpose of Use:**
        *   Verifying with a real example that **Sex / Height / Mass / Race / Limb / Side / Dominance / Subject Name** are indeed included in actual `.gt3x` files.
        *   Empirical data on "where the participant characteristics we want to modify are located."

5.  **R Package `gt3x2csv` – `read_info` / `save_header` etc.**
    *   **`read_info` Function Documentation:**
        *   Explains it "reads metadata inside the GT3X file's `info.txt` into a data.frame." ([rdrr.io](https://rdrr.io/github/danilodpsantos/gt3x2csv/src/R/gt3x_2_csv.R?utm_source=chatgpt.com "danilodpsantos/gt3x2csv source: R/gt3x_2_csv.R"))
    *   **Purpose of Use:**
        *   Confirming that the method of opening `info.txt` as text and parsing key-values is widely used.
        *   Determining that R implementations would be good references when modifying `info.txt` in Python code later.

### (3) Python Related References

6.  **`actigraph/pygt3x` GitHub Repository (Overview Level)**
    *   ActiGraph's GitHub account introduction page describes `pygt3x` as a "Python module for reading GT3X/AGDC file format data". ([GitHub](https://github.com/actigraph?utm_source=chatgpt.com "ActiGraph"))
    *   **Purpose of Use:**
        *   Confirming that the official Python module focuses on **"reading"**.
        *   Basis for judging that "modifying metadata and repacking into `.gt3x`" is not currently supported by official libraries and requires direct handling of binary/JSON/checksums.

---

## Summary

*   **Regarding `.agd`:**
    *   Based on ActiLife 5/6 Manuals + ActiLifeManual GitHub + `activAnalyzer` / `actigraph.sleepr` documentation, we understood the "AGD = SQLite DB" structure and table composition (`data`, `settings`, `sleep`, ...). ([dl.theactigraph.com](https://dl.theactigraph.com/ActiLife5-PUB10DOC10-F.pdf?utm_source=chatgpt.com "ActiLife 5 -User's Manual"))

*   **Regarding `.gt3x`:**
    *   Based on ActiGraph's official `GT3X-File-Format` / `NHANES-GT3X-File-Format` documents,
    *   R packages `read.gt3x`, `SummarizedActigraphy`, `gt3x2csv` examples and help files,
    *   and `Metadata.md` (METADATA Packet – ID 6) specifications,
    *   we established that `.gt3x` is a zip structure (`log.bin` + `info.txt` + (old version) `metadata`),
    *   and that Serial Number, Subject Name, Sex, Height, Weight (Mass), Race, Limb, Side, Dominance, etc., are stored via `info.txt` + log.bin METADATA JSON. ([GitHub](https://github.com/actigraph/NHANES-GT3X-File-Format?utm_source=chatgpt.com "actigraph/NHANES-GT3X-File-Format"))

When planning the modification code later, based on the documents above, the design will be structured as:

*   **.agd**: **Update SQLite tables → Use file as is.**
*   **.gt3x**: **Unzip → Text modify `info.txt` + Modify METADATA JSON if necessary → Re-zip.**
