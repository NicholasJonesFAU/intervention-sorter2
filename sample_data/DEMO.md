# Academic Intervention Sorter — Demo Pack

This folder contains fully synthetic sample files for demonstrating the app without using real student data.

## Files Included

**Sample data** (`sample_data/`)
- `progress_report_sample.csv` — 311 synthetic at-risk rows across 120 students
- `contact_report_sample.xlsx` — matching phone/email records
- `group_control.txt` — control file defining 3 groups in priority order
- `group_files/First_Year.xlsx` — 30 student IDs
- `group_files/STEM.xlsx` — 27 student IDs (2-student overlap with First_Year tests first-match-wins)
- `group_files/Probation.xlsx` — 20 student IDs

**Test data** (`test_data/`) — used by `test_pipeline.py`
- `progress_report.xlsx`, `contact_report.xlsx`
- `groups/athletes.xlsx`, `groups/probation.xlsx`, `groups/honors.xlsx`, `groups/international.xlsx`
- `control.txt`

---

## How to Run the Demo

1. Start the app:
   ```bash
   python main.py
   ```

2. On the **Progress Report Sorter** tab, select:

   | App Field | Demo File |
   |---|---|
   | Progress Report | `sample_data/progress_report_sample.csv` |
   | Contact Report | `sample_data/contact_report_sample.xlsx` |
   | Group Control File | `sample_data/group_control.txt` |
   | Group Files Folder | `sample_data/group_files/` |
   | Output Folder | any local folder, e.g. `output/` |

3. Click **Pre-Run Check** first to validate all files.

4. Click **Run Full Processing** to generate the output workbook.

---

## What This Demonstrates

- Reading a progress report and filtering to at-risk students only
- Normalizing student IDs (`Z12345678.0` → `Z12345678`)
- Enriching records with phone and email from the contact report
- Applying priority-ordered group matching (first-match-wins)
- Generating a styled Excel workbook with one tab per group
- QA_Log and Processing_Manifest tabs for audit trail

## Privacy Note

All data in this demo pack is fictional. Do not commit real student data, reports, outputs, or logs to GitHub.
