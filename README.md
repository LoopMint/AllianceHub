# Corporate Visits AI

Corporate Visits AI is a simple Streamlit CRM app for school departments that manage corporate partners across colleges. It helps users upload Excel or CSV partner databases, clean inconsistent headers, edit partner records, and generate topline management views.

## Features

- Upload Excel or CSV files with flexible headers such as `Company`, `Faculty`, `Visits`, `Email Opens`, `Donations`, or `Pipeline Value`.
- Maintain partner details in a CRM-style editable table.
- View top partners, cold partners to review or drop, donations, opportunities, event attendance, campus visits, email engagement, and pipeline value.
- Filter by college, department, and status.
- Configure what counts as a cold partner, including low email opens, low event attendance, low campus visits, stale contact gaps, and score thresholds.
- Ask plain-English questions such as:
  - `Who are our top 5 partners?`
  - `Which college has more partners?`
  - `Which partners are cold?`
  - `Show donations by college`
  - `How many opportunities were created?`
  - `Which partners visited campus most?`
- Export the current CRM database to Excel or CSV, including records added manually in Partner CRM.
- Export an Excel analysis workbook with partner scores, college summary, and cold-review sheets.
- Download an Excel template for departments that want a clean starting format.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app will create a local `data/partners_database.csv` file the first time it runs. This file stores CRM updates made through the interface. It also creates `data/cold_rules.json` after cold partner settings are saved.

## Expected Data Fields

The app standardizes uploaded files into these fields:

- Partner Name
- College
- Department
- Contact Name
- Email
- Phone
- Events Attended
- Campus Visits
- Emails Opened
- Emails Sent
- Donations Made
- Opportunities Created
- Opportunity Value
- Last Contact Date
- Status
- Notes

Your uploaded spreadsheet does not need to use these exact headers. The app recognizes common alternatives, for example `Company Name`, `Faculty`, `Meetings`, `Email Opens`, `Donation Amount`, and `Pipeline Value`.

## Scoring

Partners are ranked with an engagement score based on event attendance, campus visits, email activity, opportunities, and donation activity. The score is used to classify partners as:

- `Hot - priority`
- `Warm - nurture`
- `Cold - review/drop`

This is intentionally transparent and easy to adjust in `app.py` if your school wants different scoring weights.

## Ask AI Behavior

Ask AI is designed for management-style questions. It starts with a direct answer first, then shows a supporting chart or table only when useful. For example, `Which college has more partners?` returns the single leading college instead of only showing a table.
