"""
generate_test_data.py — Generates synthetic input files for testing the pipeline.

Creates:
  test_data/
      progress_report.xlsx
      contact_report.xlsx
      groups/
          athletes.xlsx
          probation.xlsx
          honors.xlsx
          international.xlsx
      control.txt

Column names match the defaults in utils/config.py.
Run:  python generate_test_data.py
"""

import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

SEED = 42
random.seed(SEED)

TEST_DIR = Path(__file__).parent / "test_data"
GROUP_DIR = TEST_DIR / "groups"
TEST_DIR.mkdir(exist_ok=True)
GROUP_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Student pool
# ---------------------------------------------------------------------------
NUM_STUDENTS = 80
student_ids = [f"Z{10000000 + i:08d}" for i in range(1, NUM_STUDENTS + 1)]

FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Morgan",
    "Casey",
    "Riley",
    "Jamie",
    "Avery",
    "Cameron",
    "Blake",
    "Drew",
    "Quinn",
    "Reese",
    "Skylar",
    "Peyton",
    "Kendall",
    "Hayden",
    "Logan",
    "Dakota",
    "Emery",
    "Maria",
    "Carlos",
    "Wei",
    "Priya",
    "Dimitri",
    "Fatima",
    "Kwame",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
]

student_names = {
    sid: f"{random.choice(LAST_NAMES)}, {random.choice(FIRST_NAMES)}"
    for sid in student_ids
}

COURSES = [
    "MAC1105",
    "ENC1101",
    "CHM2045",
    "BSC1010",
    "PSY2012",
    "STA2023",
    "COP2210",
    "PHI2010",
    "ART1300",
    "MUS1010",
    "SLS1501",
    "SOC2000",
    "ECO2013",
    "HIS1010",
    "GEA2000",
]

GRADES = ["D", "F", "C-", "D+", "F", "D-", "W", "C"]

ALERT_REASONS = [
    "Missing assignments",
    "Multiple absences",
    "Low exam scores",
    "Has not attended recently",
    "Failing multiple assessments",
    "No contact from student",
]

COMMENTS = [
    "Student has not responded to outreach.",
    "Spoke with student — aware of situation.",
    "Referred to tutoring center.",
    "Student reports family emergency.",
    "",
    "",
]

# Vary At-Risk flag values to exercise normalization
AT_RISK_VALUES = ["TRUE", "True", "true", "YES", "Yes", "Y", "1"]


# ---------------------------------------------------------------------------
# Progress Report
# Column names match PROGRESS_REPORT_COLUMN_MAP in utils/config.py
# ---------------------------------------------------------------------------
rows = []
for sid in student_ids:
    n_courses = random.choices([1, 2, 3, 4], weights=[30, 35, 25, 10])[0]
    courses = random.sample(COURSES, n_courses)
    for course in courses:
        rows.append(
            {
                "Student Name": student_names[sid],
                # Occasionally add .0 suffix to test ID normalization
                "Student ID": sid if random.random() > 0.05 else f"{sid}.0",
                "Course Name": course,
                "Marked At-Risk": AT_RISK_VALUES[len(rows) % len(AT_RISK_VALUES)],
                "Alert Reasons": random.choice(ALERT_REASONS),
                "Progress Report Grade": random.choice(GRADES),
                "Progress Report Number of Absences": random.randint(0, 12),
                "Progress Report Comment": random.choice(COMMENTS),
            }
        )

# Non-at-risk rows — should be filtered out by the pipeline
for i in range(20):
    sid = random.choice(student_ids[:20])
    rows.append(
        {
            "Student Name": student_names[sid],
            "Student ID": sid,
            "Course Name": random.choice(COURSES),
            "Marked At-Risk": "FALSE",
            "Alert Reasons": "",
            "Progress Report Grade": "B",
            "Progress Report Number of Absences": 1,
            "Progress Report Comment": "",
        }
    )

# Duplicate row — should be deduplicated by the pipeline
rows.append(
    {
        "Student Name": student_names[student_ids[0]],
        "Student ID": student_ids[0],
        "Course Name": "MAC1105",
        "Marked At-Risk": "TRUE",
        "Alert Reasons": "Duplicate row test",
        "Progress Report Grade": "D",
        "Progress Report Number of Absences": 3,
        "Progress Report Comment": "",
    }
)

progress_df = pd.DataFrame(rows)
progress_path = TEST_DIR / "progress_report.xlsx"
progress_df.to_excel(progress_path, index=False)
print(f"✓ Progress report: {len(progress_df)} rows → {progress_path}")


# ---------------------------------------------------------------------------
# Contact Report
# Column names match CONTACT_REPORT_COLUMN_MAP in utils/config.py
# ---------------------------------------------------------------------------
contact_rows = []
for sid in student_ids:
    has_contact = random.random() > 0.1  # ~10% missing contact
    contact_rows.append(
        {
            "ZNUMBER": sid,
            "CELLULAR_PHONE": (
                f"(954) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
                if has_contact
                else ""
            ),
            "LOCAL_PHONE": "",
            "PERMANENT_PHONE": (
                f"(561) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
                if has_contact and random.random() > 0.5
                else ""
            ),
            "FAU_EMAIL_ADDRESS": (
                f"{sid.lower()}@student.fau.edu" if has_contact else ""
            ),
        }
    )

contact_df = pd.DataFrame(contact_rows)
contact_path = TEST_DIR / "contact_report.xlsx"
contact_df.to_excel(contact_path, index=False)
print(f"✓ Contact report: {len(contact_df)} rows → {contact_path}")


# ---------------------------------------------------------------------------
# Group files
# Intentional 2-student overlap between athletes and probation to verify
# that first-match-wins logic works correctly.
# ---------------------------------------------------------------------------
shuffled = student_ids[:]
random.shuffle(shuffled)

athletes = shuffled[:12]
probation = shuffled[10:22]  # overlaps athletes by 2
honors = shuffled[20:30]
international = shuffled[28:38]


def write_group_file(path: Path, ids: list) -> None:
    pd.DataFrame({"Student ID": ids}).to_excel(path, index=False)
    print(f"✓ Group file: {len(ids)} IDs → {path}")


write_group_file(GROUP_DIR / "athletes.xlsx", athletes)
write_group_file(GROUP_DIR / "probation.xlsx", probation)
write_group_file(GROUP_DIR / "honors.xlsx", honors)
write_group_file(GROUP_DIR / "international.xlsx", international)


# ---------------------------------------------------------------------------
# Control file
# ---------------------------------------------------------------------------
control_content = (
    "Athletes|athletes.xlsx\n"
    "Probation|probation.xlsx\n"
    "Honors|honors.xlsx\n"
    "International|international.xlsx\n"
)
control_path = TEST_DIR / "control.txt"
control_path.write_text(control_content, encoding="utf-8")
print(f"✓ Control file → {control_path}")

print("\n✅  All test data generated successfully.")
print(f"   Test data directory: {TEST_DIR}")
