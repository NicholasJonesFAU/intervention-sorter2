# Academic Intervention Sorter

A desktop workflow tool for academic advisors that turns raw at-risk student exports from Navigate/EAB into ready-to-use Excel intervention lists — matched to advisor caseloads, enriched with contact information, and organized by priority group. No manual filtering, no copy-pasting, no pivot tables.

Built for the **FAU Academic Advising** team and modeled on the real operational workflow of running progress-report campaigns across a full semester.

---

## The Problem It Solves

At a large research university, a progress-report campaign can flag 2,000+ at-risk students at once. The advising team needs to divide that list by student population (athletes handled differently than honors students, probation students differently than general population), ensure no student is contacted twice in the same campaign, and get phone and email into the same row so advisors can make calls immediately.

Doing this by hand in Excel takes 30–60 minutes per checkpoint and introduces errors every time. This tool does it in under a minute with a full audit trail.

---

## Key Features

### Progress Report Sorter
- Loads Navigate/EAB progress report exports in `.xlsx` or `.csv`
- Filters to at-risk students only — supports `TRUE / Yes / Y / 1` flag variants
- Aggregates multiple at-risk courses into one row per student
- Assigns each student to their first matching group via a **priority-ordered group list** — first match wins, exactly like advisor caseload routing rules
- Unmatched students fall to `Risk_1_2` (1–2 at-risk courses) or `Risk_3_Plus` (3+) automatically
- Merges phone and email from a separate contact report — phone fallback chain: cellular → local → permanent
- **Exclude-previous checkbox**: reads/writes a persisted `assigned_students.txt` so students contacted in PR1 are not in the PR2 list unless re-flagged
- **Group Selection dialog**: choose which groups to produce per run without editing any files
- **Pre-Run Check**: validates file formats, column presence, and group-file coverage before committing to a full run

### Midterm Sorter
- Same group-matching pipeline applied to Canvas midterm grade exports
- At-risk threshold: C− or below — W and WM excluded by design

### Faculty Report Status
- Analyzes which professors have submitted progress reports
- Completion % by college, department, and individual professor
- Output workbook includes summary charts and a Faculty Download tab for follow-up

### Campaign Trend
- Analyzes student population movement across PR1 → Midterm → PR2
- Trajectory categories: Persistent, Recovered Early, Recovered Late, Relapsed, New Late, and more
- Master Season Report: combined end-of-semester workbook with full student list and season summary

### Campaigns (Semester Manager)
- Create and name a semester — all runs are organized under it automatically
- **Configure groups directly in the app** — add group files in priority order on the Campaigns tab; no control file required once groups are configured
- **Copy from Previous Semester**: carry over group names and re-point to new files each term
- Checkpoint cards (PR1 / Midterm / PR2) show run count, student totals, and status at a glance
- File paths saved on first run and pre-filled for all subsequent runs in the same semester
- Full run history preserved across semesters

### Settings
- Column name mapping for all four input file types — no code changes required
- Changes saved to `settings.json`, take effect on the next run

---

## Output Workbook Structure

| Tab | Contents |
|---|---|
| **Summary** | Processing metrics, run timestamp, group counts, contact coverage rate |
| **[Group name]** | One tab per configured group |
| **Risk\_1\_2** | Unmatched students with 1–2 at-risk courses |
| **Risk\_3\_Plus** | Unmatched students with 3+ at-risk courses |
| **Missing\_Contacts** | Students where no phone or email was found |
| **QA\_Log** | All data quality events — column mismatches, duplicate IDs, skipped rows |
| **Processing\_Manifest** | Full run metadata: input file names, timestamps, row counts, settings snapshot |

---

## Setup

```bash
pip install -r requirements.txt
python main.py
```

**Requirements:** Python 3.10+, Windows (tkinter GUI). Tested on Windows 10/11.

### Run headless tests (no GUI)
```bash
python generate_test_data.py   # generate synthetic test files (one-time)
python test_pipeline.py        # runs 3 test suites: validation, full run, semester groups
```

### Load demo data in the app
Click **Load Demo Files** on the Progress Report Sorter tab. Loads synthetic data from `sample_data/` and pre-fills all file pickers so you can click Run immediately.

---

## Input Files

| File | Format | Required Columns |
|---|---|---|
| Progress Report | `.xlsx` / `.csv` | `Student Name`, `Student ID`, `Course Name`, `Marked At-Risk` |
| Contact Report | `.xlsx` | `ZNUMBER`, `CELLULAR_PHONE`, `FAU_EMAIL_ADDRESS` |
| Group Control File | `.txt` | `TabName\|filename.xlsx` one per line (optional if semester groups configured) |
| Group Files Folder | folder | `.xlsx` files listed in the control file (optional if semester groups configured) |

Column names are configurable in the Settings tab — no code changes needed.

---

## Control File Format

```
Athletes|athletes.xlsx
Probation|probation.xlsx
Honors|honors.xlsx
International|international.xlsx
```

- **Order matters** — first match wins
- Lines starting with `#` are comments; blank lines are ignored
- **Optional** when groups are configured on the Campaigns tab

---

## Student ID Normalization

All student IDs are normalized before any matching:

- Converted to string, stripped of whitespace, uppercased
- `.0` Excel decimal artifacts removed (`Z12345678.0` → `Z12345678`)

---

## At-Risk Flag Values Recognized

`TRUE` / `True` / `true` / `YES` / `Yes` / `Y` / `1`

---

## Architecture

The codebase enforces strict separation between the GUI layer and all business logic. The GUI never processes data — it collects file paths, shows progress, and renders results. Every processor module is independently testable (see `test_pipeline.py`).

```
main.py                              ← App entry point — assembles the window,
                                       delegates everything to gui_* modules

gui_theme.py                         ← Color constants, font loading, button presets
gui_widgets.py                       ← RoundedButton, FilePickerRow, section_label
gui_dialogs.py                       ← Group selection, season setup, new semester dialogs
gui_logging.py                       ← Shared log-box helpers
gui_progress_tab.py                  ← Progress Report Sorter tab layout
gui_progress_actions.py              ← Progress Report run/validate/precheck handlers
gui_report_status_tab.py             ← Faculty Report Status tab layout
gui_report_status_actions.py         ← Faculty report run handler
gui_midterm_tab.py                   ← Midterm Sorter tab layout
gui_midterm_actions.py               ← Midterm run handler
gui_trend_tab.py                     ← Campaign Trend tab layout
gui_trend_actions.py                 ← Trend report and master season report handlers
gui_campaign_tab.py                  ← Campaigns tab layout
gui_campaign_actions.py              ← Semester lifecycle, group management, checkpoints
gui_settings_tab.py                  ← Settings tab layout and save/reset handlers
gui_help_tab.py                      ← Help/About tab
gui_demo.py                          ← Demo mode: loads synthetic sample data

gui/
    theme.py                         ← Canonical color and button-style reference

processors/
    pipeline_controller.py           ← Orchestrator: sequences all pipeline steps
    grade_processor.py               ← Load / filter / deduplicate progress report
    contact_processor.py             ← Load and merge contact report
    aggregator.py                    ← Collapse courses → one row per student
    group_matcher.py                 ← First-match-wins group assignment;
                                       supports both control-file and semester-groups paths
    exporter.py                      ← Build styled output workbook with charts
    midterm_pipeline_controller.py   ← Midterm orchestrator
    midterm_processor.py             ← Load and filter Canvas grade export
    midterm_aggregator.py            ← Course aggregation for midterm
    trend_analyzer.py                ← Cross-checkpoint population analysis
    trend_exporter.py                ← Trend report workbook builder
    report_status_processor.py       ← Faculty submission analysis
    report_status_exporter.py        ← Faculty report workbook with charts
    season_report.py                 ← End-of-semester master report generator
    semester_manager.py              ← Semester lifecycle, group config, run history (JSON)
    campaign_manager.py              ← Assigned-student persistence
    prerun_checker.py                ← Pre-flight data quality validation
    summary_enhancer.py              ← Summary tab chart and metric generation
    department_mapper.py             ← Course prefix → college/department mapping

utils/
    config.py                        ← All configurable values — one place
    normalization.py                 ← ID, flag, and string normalization
    validation.py                    ← File and column validation
    logging_utils.py                 ← Logger setup and QALog event collector
    excel_utils.py                   ← openpyxl formatting helpers
    settings_manager.py              ← Runtime settings with JSON persistence

sample_data/                         ← Synthetic demo files (load via Demo button)
test_data/                           ← Synthetic files for test_pipeline.py
output/                              ← Generated workbooks (organized by semester)
logs/                                ← Timestamped run logs
```

### Design decisions worth noting

**GUI/logic decoupling.** `main.py` and the `gui_*` modules never touch pandas or openpyxl. All file I/O, data transformations, and Excel generation happen in the processors layer. The GUI thread never blocks — processing runs in a daemon thread with `self.after()` callbacks for UI updates.

**First-match-wins group routing.** The group list defines a priority queue. A student in the Athletes file who is also on probation appears only in Athletes — matching how advisor caseloads are structured. The order is owned by operations staff, not developers.

**Semester-configured groups.** Groups can be configured directly in the Campaigns tab (name + file path + priority order) and persist with the semester record. When semester groups are set, the control file and group folder pickers are optional. This lets coordinators set up groups once per semester rather than maintaining a separate text file.

**QA\_Log tab.** Every data quality event lands in the output workbook itself — a reproducible audit trail attached to each intervention file, not a log file that might get lost.

**Settings as runtime config.** Column names vary across Navigate export versions and institutional customizations. `settings.json` lets an administrator update column mappings through the Settings tab without touching Python.

---

## Tech Stack

| Layer | Technology |
|---|---|
| GUI | Python `tkinter` + `ttk` — no external UI dependencies |
| Data processing | `pandas` — normalization, deduplication, merge, group assignment |
| Excel output | `openpyxl` — styled workbooks with charts, conditional formatting, freeze panes |
| Charts | `matplotlib` — embedded into openpyxl worksheets |
| Persistence | JSON — semester state, run history, settings |
| Logging | Python `logging` + custom QALog collector |

---

## Background

This tool was built to solve a real operational pain point in a higher education advising office. The workflow it automates — loading Navigate exports, matching students to advisor caseloads, merging contact data, producing intervention lists — is a task that advisors at large universities run multiple times per semester, under time pressure, at the start of intervention windows when speed matters most.

The design prioritizes **reliability over cleverness**: deterministic group assignment, explicit audit logs, pre-run validation, and settings that non-developers can manage. The goal is that an advising coordinator with no programming background can configure and run this tool confidently.

---

*Python 3.10+ · pandas · openpyxl · matplotlib · tkinter*
