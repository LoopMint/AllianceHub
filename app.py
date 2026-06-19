import io
import json
import re
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


APP_TITLE = "Corporate Visits AI"
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "partners_database.csv"
SETTINGS_FILE = DATA_DIR / "cold_rules.json"


CANONICAL_FIELDS = {
    "partner_name": {
        "label": "Partner Name",
        "aliases": ["partner", "partner name", "company", "company name", "organisation", "organization", "account", "customer", "client", "institution"],
        "default": "",
    },
    "college": {
        "label": "College",
        "aliases": ["college", "faculty", "school", "division", "campus"],
        "default": "",
    },
    "department": {
        "label": "Department",
        "aliases": ["department", "dept", "unit", "programme", "program"],
        "default": "",
    },
    "contact_name": {
        "label": "Contact Name",
        "aliases": ["contact", "contact name", "pic", "person in charge", "representative"],
        "default": "",
    },
    "email": {
        "label": "Email",
        "aliases": ["email", "email address", "e-mail", "mail"],
        "default": "",
    },
    "phone": {
        "label": "Phone",
        "aliases": ["phone", "phone number", "mobile", "telephone", "contact number"],
        "default": "",
    },
    "events_attended": {
        "label": "Events Attended",
        "aliases": ["events attended", "event attendance", "attended events", "events", "no of events", "number of events"],
        "default": 0,
    },
    "campus_visits": {
        "label": "Campus Visits",
        "aliases": ["campus visits", "visits", "visit count", "meetings", "campus meeting", "meeting count"],
        "default": 0,
    },
    "emails_opened": {
        "label": "Emails Opened",
        "aliases": ["emails opened", "email opened", "open email", "opened emails", "email opens", "opens"],
        "default": 0,
    },
    "emails_sent": {
        "label": "Emails Sent",
        "aliases": ["emails sent", "email sent", "communications", "email communications", "email count", "sent emails"],
        "default": 0,
    },
    "donations_made": {
        "label": "Donations Made",
        "aliases": ["donations made", "donation", "donations", "donation amount", "amount donated", "gift amount"],
        "default": 0.0,
    },
    "opportunities_created": {
        "label": "Opportunities Created",
        "aliases": ["opportunities created", "opportunities", "opportunity", "deals", "projects", "pipeline"],
        "default": 0,
    },
    "opportunity_value": {
        "label": "Opportunity Value",
        "aliases": ["opportunity value", "pipeline value", "deal value", "project value", "value"],
        "default": 0.0,
    },
    "last_contact_date": {
        "label": "Last Contact Date",
        "aliases": ["last contact date", "last contact", "last engagement", "last activity", "last meeting date"],
        "default": "",
    },
    "status": {
        "label": "Status",
        "aliases": ["status", "stage", "relationship status", "partner status"],
        "default": "Active",
    },
    "notes": {
        "label": "Notes",
        "aliases": ["notes", "remarks", "comments", "summary"],
        "default": "",
    },
}

NUMERIC_FIELDS = [
    "events_attended",
    "campus_visits",
    "emails_opened",
    "emails_sent",
    "donations_made",
    "opportunities_created",
    "opportunity_value",
]

DEFAULT_COLD_RULES = {
    "cold_score_max": 12,
    "hot_score_min": 35,
    "min_email_opens": 2,
    "min_events_attended": 1,
    "min_campus_visits": 1,
    "stale_days": 120,
    "include_stale_gap": True,
    "include_low_email": True,
    "include_low_events": True,
    "include_low_visits": False,
}


def slug(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).strip().lower()).strip()


def money(value):
    try:
        return f"${float(value):,.0f}"
    except Exception:
        return "$0"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def sample_data():
    today = date.today()
    return pd.DataFrame(
        [
            {
                "partner_name": "Northstar Bank",
                "college": "Business",
                "department": "Career Services",
                "contact_name": "Alicia Tan",
                "email": "alicia.tan@example.com",
                "phone": "+1 555 0101",
                "events_attended": 9,
                "campus_visits": 4,
                "emails_opened": 17,
                "emails_sent": 22,
                "donations_made": 45000,
                "opportunities_created": 5,
                "opportunity_value": 120000,
                "last_contact_date": today.replace(month=max(1, today.month - 1)).isoformat(),
                "status": "Active",
                "notes": "Strong internship pipeline and scholarship interest.",
            },
            {
                "partner_name": "Helio Robotics",
                "college": "Engineering",
                "department": "Industry Relations",
                "contact_name": "Marcus Reed",
                "email": "m.reed@example.com",
                "phone": "+1 555 0102",
                "events_attended": 6,
                "campus_visits": 3,
                "emails_opened": 12,
                "emails_sent": 15,
                "donations_made": 20000,
                "opportunities_created": 4,
                "opportunity_value": 90000,
                "last_contact_date": today.isoformat(),
                "status": "Active",
                "notes": "Interested in capstone sponsorship.",
            },
            {
                "partner_name": "Lakeside Clinic Group",
                "college": "Health Sciences",
                "department": "External Partnerships",
                "contact_name": "Priya Shah",
                "email": "pshah@example.com",
                "phone": "+1 555 0103",
                "events_attended": 4,
                "campus_visits": 2,
                "emails_opened": 9,
                "emails_sent": 13,
                "donations_made": 10000,
                "opportunities_created": 2,
                "opportunity_value": 30000,
                "last_contact_date": today.isoformat(),
                "status": "Active",
                "notes": "Clinical placement discussion ongoing.",
            },
            {
                "partner_name": "Blue Harbor Retail",
                "college": "Business",
                "department": "Alumni Relations",
                "contact_name": "Noah Chen",
                "email": "noah.chen@example.com",
                "phone": "+1 555 0104",
                "events_attended": 1,
                "campus_visits": 0,
                "emails_opened": 1,
                "emails_sent": 8,
                "donations_made": 0,
                "opportunities_created": 0,
                "opportunity_value": 0,
                "last_contact_date": "2025-11-15",
                "status": "Cold",
                "notes": "Low response after repeated outreach.",
            },
        ]
    )


def load_data():
    ensure_data_dir()
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE).fillna("")
    df = sample_data()
    save_data(df)
    return df


def save_data(df):
    ensure_data_dir()
    clean = clean_dataframe(df)
    clean.to_csv(DATA_FILE, index=False)


def load_cold_rules():
    ensure_data_dir()
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            saved = json.load(file)
        return {**DEFAULT_COLD_RULES, **saved}
    return DEFAULT_COLD_RULES.copy()


def save_cold_rules(rules):
    ensure_data_dir()
    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(rules, file, indent=2)


def clean_dataframe(df):
    clean = df.copy().fillna("")
    for field, meta in CANONICAL_FIELDS.items():
        if field not in clean.columns:
            clean[field] = meta["default"]
    for field in NUMERIC_FIELDS:
        clean[field] = (
            clean[field]
            .astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .replace({"": "0", "nan": "0", "None": "0"})
        )
        clean[field] = pd.to_numeric(clean[field], errors="coerce").fillna(0)
    clean["last_contact_date"] = pd.to_datetime(clean["last_contact_date"], errors="coerce").dt.date.astype(str)
    clean["last_contact_date"] = clean["last_contact_date"].replace("NaT", "")
    clean["status"] = clean["status"].replace("", "Active")
    return clean[list(CANONICAL_FIELDS.keys())]


def normalize_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    raw = pd.read_csv(uploaded_file) if name.endswith(".csv") else pd.read_excel(uploaded_file)

    alias_to_field = {}
    for field, meta in CANONICAL_FIELDS.items():
        alias_to_field[slug(field)] = field
        alias_to_field[slug(meta["label"])] = field
        for alias in meta["aliases"]:
            alias_to_field[slug(alias)] = field

    rename_map = {}
    for column in raw.columns:
        normalized = slug(column)
        if normalized in alias_to_field:
            rename_map[column] = alias_to_field[normalized]

    df = raw.rename(columns=rename_map)
    output = pd.DataFrame()
    for field, meta in CANONICAL_FIELDS.items():
        if field in df.columns:
            series = df[field]
            output[field] = series.iloc[:, 0] if isinstance(series, pd.DataFrame) else series
        else:
            output[field] = meta["default"]
    return clean_dataframe(output)


def days_since_contact(series):
    parsed = pd.to_datetime(series, errors="coerce")
    return (pd.Timestamp(date.today()) - parsed).dt.days


def score_partners(df, rules=None):
    rules = rules or load_cold_rules()
    scored = clean_dataframe(df)
    scored["days_since_contact"] = days_since_contact(scored["last_contact_date"]).fillna(9999).astype(int)
    scored["engagement_score"] = (
        scored["events_attended"] * 4
        + scored["campus_visits"] * 5
        + scored["emails_opened"] * 1.5
        + scored["emails_sent"] * 0.5
        + scored["opportunities_created"] * 4
        + np.where(scored["donations_made"] > 0, 8, 0)
    )
    cold_flags = scored["engagement_score"].le(rules["cold_score_max"])
    if rules["include_low_email"]:
        cold_flags = cold_flags | scored["emails_opened"].lt(rules["min_email_opens"])
    if rules["include_low_events"]:
        cold_flags = cold_flags | scored["events_attended"].lt(rules["min_events_attended"])
    if rules["include_low_visits"]:
        cold_flags = cold_flags | scored["campus_visits"].lt(rules["min_campus_visits"])
    if rules["include_stale_gap"]:
        cold_flags = cold_flags | scored["days_since_contact"].gt(rules["stale_days"])

    scored["temperature"] = np.select(
        [cold_flags, scored["engagement_score"].ge(rules["hot_score_min"])],
        ["Cold - review/drop", "Hot - priority"],
        default="Warm - nurture",
    )
    scored["cold_reason"] = scored.apply(lambda row: cold_reason(row, rules), axis=1)
    return scored.sort_values("engagement_score", ascending=False)


def cold_reason(row, rules):
    reasons = []
    if row["engagement_score"] <= rules["cold_score_max"]:
        reasons.append("low total engagement")
    if rules["include_low_email"] and row["emails_opened"] < rules["min_email_opens"]:
        reasons.append("low email opens")
    if rules["include_low_events"] and row["events_attended"] < rules["min_events_attended"]:
        reasons.append("low event attendance")
    if rules["include_low_visits"] and row["campus_visits"] < rules["min_campus_visits"]:
        reasons.append("low campus visits")
    if rules["include_stale_gap"] and row["days_since_contact"] > rules["stale_days"]:
        reasons.append("stale contact gap")
    return ", ".join(reasons) if reasons else "healthy engagement"


def to_excel_bytes(df, include_analysis=True, rules=None):
    rules = rules or load_cold_rules()
    scored = score_partners(df, rules)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        clean_dataframe(df).to_excel(writer, sheet_name="Partner CRM", index=False)
        if include_analysis:
            scored.to_excel(writer, sheet_name="Scored Partners", index=False)
            college_summary(scored).to_excel(writer, sheet_name="College Summary", index=False)
            scored[scored["temperature"].eq("Cold - review/drop")].to_excel(writer, sheet_name="Cold Review", index=False)
    return output.getvalue()


def college_summary(scored):
    return (
        scored.groupby("college", dropna=False)
        .agg(
            partners=("partner_name", "count"),
            average_engagement=("engagement_score", "mean"),
            events_attended=("events_attended", "sum"),
            campus_visits=("campus_visits", "sum"),
            email_opens=("emails_opened", "sum"),
            donations_made=("donations_made", "sum"),
            opportunities_created=("opportunities_created", "sum"),
            opportunity_value=("opportunity_value", "sum"),
        )
        .reset_index()
        .sort_values(["partners", "average_engagement"], ascending=False)
    )


def apply_style():
    st.markdown(
        """
        <style>
        :root {
            --navy: #10243e;
            --ink: #172033;
            --muted: #5c6678;
            --line: #d8dee8;
            --gold: #b9975b;
            --panel: #ffffff;
            --soft: #f5f7fa;
        }
        .stApp {
            background: #f4f6f9;
            color: var(--ink);
        }
        .block-container {
            padding-top: 1.1rem;
            max-width: 1440px;
        }
        h1, h2, h3 {
            color: var(--navy);
            letter-spacing: 0;
        }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-top: 4px solid var(--gold);
            padding: 16px 18px;
            border-radius: 8px;
            box-shadow: 0 8px 22px rgba(16, 36, 62, 0.05);
        }
        div[data-testid="stMetricLabel"] {
            color: var(--muted);
        }
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--line);
        }
        .executive-band {
            background: var(--navy);
            color: #ffffff;
            padding: 18px 22px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .executive-band h1 {
            color: #ffffff;
            margin-bottom: 4px;
        }
        .executive-band p {
            color: #dfe6ef;
            margin: 0;
        }
        .insight-box {
            background: #ffffff;
            border: 1px solid var(--line);
            border-left: 4px solid var(--gold);
            border-radius: 8px;
            padding: 14px 16px;
            margin: 10px 0 16px;
        }
        div[role="radiogroup"] label {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 7px 10px;
            background: #ffffff;
            margin-bottom: 6px;
        }
        button[kind="primary"] {
            background: var(--navy);
            border-color: var(--navy);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def filter_data(df):
    with st.sidebar:
        st.markdown("### Filters")
        colleges = sorted([x for x in df["college"].dropna().unique() if str(x).strip()])
        departments = sorted([x for x in df["department"].dropna().unique() if str(x).strip()])
        college_filter = st.multiselect("College", colleges)
        department_filter = st.multiselect("Department", departments)
        status_filter = st.multiselect("Status", sorted(df["status"].dropna().unique()))

    filtered = df.copy()
    if college_filter:
        filtered = filtered[filtered["college"].isin(college_filter)]
    if department_filter:
        filtered = filtered[filtered["department"].isin(department_filter)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]
    return filtered


def metric_row(scored):
    left, middle, right, fourth, fifth = st.columns(5)
    left.metric("Partners", f"{len(scored):,}")
    middle.metric("Donations", money(scored["donations_made"].sum()))
    right.metric("Opportunities", f"{int(scored['opportunities_created'].sum()):,}")
    fourth.metric("Pipeline Value", money(scored["opportunity_value"].sum()))
    fifth.metric("Cold Review", f"{len(scored[scored['temperature'].eq('Cold - review/drop')]):,}")


def management_module(df, rules):
    st.markdown("## Management Overview")
    scored = score_partners(df, rules)
    metric_row(scored)

    if scored.empty:
        st.info("No partner records match the current filters.")
        return

    top_partner = scored.iloc[0]
    top_college = college_summary(scored).iloc[0]
    st.markdown(
        f"""
        <div class="insight-box">
        <b>Executive readout:</b> {top_partner['partner_name']} is the highest-engagement partner.
        {top_college['college']} has the largest partner base with {int(top_college['partners'])} partner(s).
        Total giving is {money(scored['donations_made'].sum())}, with {int(scored['opportunities_created'].sum())} opportunity record(s).
        </div>
        """,
        unsafe_allow_html=True,
    )

    analysis_view = st.radio(
        "Topline analysis view",
        ["Overall engagement", "Event attendance", "Campus visits", "Donation only", "Opportunities", "Email communications"],
        horizontal=True,
    )
    rank_map = {
        "Overall engagement": ("engagement_score", "Top Partners by Engagement"),
        "Event attendance": ("events_attended", "Partners Most Often Attending Events"),
        "Campus visits": ("campus_visits", "Partners Visiting Campus Most"),
        "Donation only": ("donations_made", "Top Donors"),
        "Opportunities": ("opportunities_created", "Partners Creating Opportunities"),
        "Email communications": ("emails_opened", "Partners Opening Communications"),
    }
    rank_field, rank_title = rank_map[analysis_view]
    ranked = scored.sort_values(rank_field, ascending=False).head(10)

    col1, col2 = st.columns((1.25, 1))
    with col1:
        st.markdown(f"### {rank_title}")
        st.dataframe(
            ranked[
                [
                    "partner_name",
                    "college",
                    "department",
                    "events_attended",
                    "campus_visits",
                    "emails_opened",
                    "donations_made",
                    "opportunities_created",
                    "engagement_score",
                    "temperature",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
    with col2:
        st.markdown("### Visual Ranking")
        chart = ranked.set_index("partner_name")[[rank_field]]
        st.bar_chart(chart)

    col3, col4 = st.columns((1, 1))
    with col3:
        st.markdown("### Cold Partners To Review")
        cold = scored[scored["temperature"].eq("Cold - review/drop")].sort_values("engagement_score")
        st.dataframe(
            cold[["partner_name", "college", "department", "last_contact_date", "engagement_score", "cold_reason"]].head(10),
            use_container_width=True,
            hide_index=True,
        )
    with col4:
        st.markdown("### College Performance")
        by_college = college_summary(scored)
        st.dataframe(by_college, use_container_width=True, hide_index=True)
        st.bar_chart(by_college.set_index("college")[["partners"]])


def upload_module(existing_df, rules):
    st.markdown("## Upload Excel or CSV")
    st.write("Upload partner data even if the headers use names like Company, Faculty, Visits, Email Opens, Donations, or Pipeline Value.")
    uploaded_file = st.file_uploader("Partner database", type=["xlsx", "xls", "csv"])
    mode = st.radio("When importing", ["Replace current database", "Append to current database"], horizontal=True)
    if uploaded_file and st.button("Import Data", type="primary"):
        imported = normalize_uploaded_file(uploaded_file)
        combined = pd.concat([existing_df, imported], ignore_index=True) if mode.startswith("Append") else imported
        save_data(combined)
        st.success(f"Imported {len(imported):,} rows. Database now has {len(combined):,} partners.")
        st.rerun()

    st.markdown("### Download Current Database")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "Export Current CRM to Excel",
            data=to_excel_bytes(existing_df, include_analysis=True, rules=rules),
            file_name="corporate_visits_ai_current_database.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col2:
        csv = clean_dataframe(existing_df).to_csv(index=False).encode("utf-8")
        st.download_button("Export Current CRM to CSV", data=csv, file_name="corporate_visits_ai_current_database.csv", mime="text/csv")

    buffer = io.BytesIO()
    sample_data().to_excel(buffer, index=False)
    st.download_button(
        "Download Excel Template",
        data=buffer.getvalue(),
        file_name="corporate_visits_ai_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def editor_module(df, rules):
    st.markdown("## Partner CRM")
    st.write("Edit rows directly, add new partners at the bottom, then save. Exports use the latest saved CRM database.")
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=560,
        column_config={
            "partner_name": st.column_config.TextColumn("Partner Name", required=True),
            "college": st.column_config.TextColumn("College"),
            "department": st.column_config.TextColumn("Department"),
            "contact_name": st.column_config.TextColumn("Contact"),
            "email": st.column_config.TextColumn("Email"),
            "phone": st.column_config.TextColumn("Phone"),
            "events_attended": st.column_config.NumberColumn("Events", min_value=0, step=1),
            "campus_visits": st.column_config.NumberColumn("Campus Visits", min_value=0, step=1),
            "emails_opened": st.column_config.NumberColumn("Email Opens", min_value=0, step=1),
            "emails_sent": st.column_config.NumberColumn("Emails Sent", min_value=0, step=1),
            "donations_made": st.column_config.NumberColumn("Donations", min_value=0, step=100),
            "opportunities_created": st.column_config.NumberColumn("Opportunities", min_value=0, step=1),
            "opportunity_value": st.column_config.NumberColumn("Pipeline Value", min_value=0, step=100),
            "last_contact_date": st.column_config.TextColumn("Last Contact Date"),
            "status": st.column_config.SelectboxColumn("Status", options=["Active", "Warm", "Hot", "Cold", "Dropped"]),
            "notes": st.column_config.TextColumn("Notes"),
        },
    )
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Save Changes", type="primary"):
            save_data(edited)
            st.success("Partner database saved.")
            st.rerun()
    with col2:
        st.download_button(
            "Export Excel",
            data=to_excel_bytes(edited, include_analysis=True, rules=rules),
            file_name="corporate_visits_ai_crm_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col3:
        csv = clean_dataframe(edited).to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", data=csv, file_name="corporate_visits_ai_crm_export.csv", mime="text/csv")


def rules_module(df, rules):
    st.markdown("## Cold Partner Rules")
    st.write("Define what management considers a cold partner. These settings drive the overview, Ask AI answers, and Excel analysis export.")
    col1, col2, col3 = st.columns(3)
    with col1:
        cold_score_max = st.number_input("Cold if engagement score is at or below", min_value=0, value=int(rules["cold_score_max"]), step=1)
        hot_score_min = st.number_input("Hot if engagement score is at or above", min_value=1, value=int(rules["hot_score_min"]), step=1)
        stale_days = st.number_input("Cold if no contact after days", min_value=1, value=int(rules["stale_days"]), step=15)
    with col2:
        min_email_opens = st.number_input("Minimum email opens", min_value=0, value=int(rules["min_email_opens"]), step=1)
        min_events_attended = st.number_input("Minimum event attendance", min_value=0, value=int(rules["min_events_attended"]), step=1)
        min_campus_visits = st.number_input("Minimum campus visits", min_value=0, value=int(rules["min_campus_visits"]), step=1)
    with col3:
        include_low_email = st.checkbox("Flag low email opens", value=bool(rules["include_low_email"]))
        include_low_events = st.checkbox("Flag low event attendance", value=bool(rules["include_low_events"]))
        include_low_visits = st.checkbox("Flag low campus visits", value=bool(rules["include_low_visits"]))
        include_stale_gap = st.checkbox("Flag stale contact gap", value=bool(rules["include_stale_gap"]))

    updated = {
        "cold_score_max": cold_score_max,
        "hot_score_min": hot_score_min,
        "min_email_opens": min_email_opens,
        "min_events_attended": min_events_attended,
        "min_campus_visits": min_campus_visits,
        "stale_days": stale_days,
        "include_stale_gap": include_stale_gap,
        "include_low_email": include_low_email,
        "include_low_events": include_low_events,
        "include_low_visits": include_low_visits,
    }
    if st.button("Save Cold Rules", type="primary"):
        save_cold_rules(updated)
        st.success("Cold partner rules saved.")
        st.rerun()

    preview = score_partners(df, updated)
    st.markdown("### Rule Preview")
    st.dataframe(
        preview[["partner_name", "college", "engagement_score", "temperature", "days_since_contact", "cold_reason"]],
        use_container_width=True,
        hide_index=True,
    )


def answer_result(text, table=None, chart=None):
    return {"text": text, "table": table, "chart": chart}


def singular_top_answer(scored, group_field, metric_field, metric_label, question):
    if "more partners" in question or "most partners" in question or "largest" in question:
        grouped = (
            scored.groupby(group_field, dropna=False)
            .agg(partners=("partner_name", "count"), engagement=("engagement_score", "mean"))
            .reset_index()
            .sort_values(["partners", "engagement"], ascending=False)
        )
        if grouped.empty:
            return answer_result("No matching partner records are available.")
        top = grouped.iloc[0]
        text = f"{top[group_field]} has the most partners, with {int(top['partners'])} partner(s)."
        return answer_result(text, chart=grouped.set_index(group_field)[["partners"]].head(8))

    grouped = (
        scored.groupby(group_field, dropna=False)
        .agg(value=(metric_field, "sum"), partners=("partner_name", "count"), engagement=("engagement_score", "mean"))
        .reset_index()
        .sort_values(["value", "partners", "engagement"], ascending=False)
    )
    if grouped.empty:
        return answer_result("No matching partner records are available.")
    top = grouped.iloc[0]
    if metric_field in ["donations_made", "opportunity_value"]:
        text = f"{top[group_field]} leads by {metric_label.lower()} with {money(top['value'])}."
    else:
        text = f"{top[group_field]} leads by {metric_label.lower()} with {int(top['value'])}."
    return answer_result(text, chart=grouped.set_index(group_field)[["value"]].head(8))


def answer_question(question, df, rules):
    q = question.lower().strip()
    scored = score_partners(df, rules)
    if not q:
        return answer_result("Ask a question such as: Which college has more partners? Who are top donors? Which partners are cold?")
    if scored.empty:
        return answer_result("No partner records match the current filters.")

    if "college" in q and any(term in q for term in ["more partner", "most partner", "largest", "highest number"]):
        return singular_top_answer(scored, "college", "partner_name", "Partner count", q)
    if "department" in q and any(term in q for term in ["more partner", "most partner", "largest", "highest number"]):
        return singular_top_answer(scored, "department", "partner_name", "Partner count", q)
    if "college" in q and ("donation" in q or "donor" in q):
        return singular_top_answer(scored, "college", "donations_made", "Donations", q)
    if "college" in q and ("opportunit" in q or "pipeline" in q):
        return singular_top_answer(scored, "college", "opportunity_value", "Pipeline value", q)

    if any(term in q for term in ["cold", "drop", "inactive", "low"]):
        rows = scored[scored["temperature"].eq("Cold - review/drop")].sort_values("engagement_score")
        if rows.empty:
            return answer_result("No partners currently meet the cold-partner rules.")
        names = ", ".join(rows["partner_name"].head(5).astype(str).tolist())
        return answer_result(
            f"{len(rows)} partner(s) are cold by the current rules. First review: {names}.",
            table=rows[["partner_name", "college", "department", "last_contact_date", "engagement_score", "cold_reason"]].head(10),
        )
    if "donation" in q or "donor" in q:
        top = scored.sort_values("donations_made", ascending=False).iloc[0]
        return answer_result(
            f"Total donations are {money(scored['donations_made'].sum())}. The top donor is {top['partner_name']} with {money(top['donations_made'])}.",
            chart=scored.sort_values("donations_made", ascending=False).head(8).set_index("partner_name")[["donations_made"]],
        )
    if "opportunit" in q or "pipeline" in q:
        top = scored.sort_values("opportunity_value", ascending=False).iloc[0]
        return answer_result(
            f"There are {int(scored['opportunities_created'].sum()):,} opportunities worth {money(scored['opportunity_value'].sum())}. Largest pipeline partner: {top['partner_name']}.",
            chart=scored.sort_values("opportunity_value", ascending=False).head(8).set_index("partner_name")[["opportunity_value"]],
        )
    if "visit" in q or "meeting" in q:
        top = scored.sort_values("campus_visits", ascending=False).iloc[0]
        return answer_result(
            f"{top['partner_name']} has visited campus most, with {int(top['campus_visits'])} visit(s).",
            chart=scored.sort_values("campus_visits", ascending=False).head(8).set_index("partner_name")[["campus_visits"]],
        )
    if "event" in q or "attend" in q or "attendance" in q:
        top = scored.sort_values("events_attended", ascending=False).iloc[0]
        return answer_result(
            f"{top['partner_name']} attends events most often, with {int(top['events_attended'])} event(s).",
            chart=scored.sort_values("events_attended", ascending=False).head(8).set_index("partner_name")[["events_attended"]],
        )
    if "email" in q or "communication" in q:
        email_rank = scored.assign(total_email_activity=scored["emails_opened"] + scored["emails_sent"]).sort_values("total_email_activity", ascending=False)
        top = email_rank.iloc[0]
        return answer_result(
            f"{top['partner_name']} has the highest email activity, with {int(top['total_email_activity'])} total email touchpoint(s).",
            chart=email_rank.head(8).set_index("partner_name")[["emails_opened", "emails_sent"]],
        )
    if any(term in q for term in ["top", "best", "priority"]):
        count = int(re.search(r"\b(\d+)\b", q).group(1)) if re.search(r"\b(\d+)\b", q) else 5
        rows = scored.head(count)
        names = ", ".join(rows["partner_name"].astype(str).tolist())
        return answer_result(
            f"The top {len(rows)} partner(s) by engagement are {names}.",
            table=rows[["partner_name", "college", "department", "engagement_score", "temperature"]].head(count),
            chart=rows.set_index("partner_name")[["engagement_score"]],
        )
    if "college" in q:
        top = college_summary(scored).iloc[0]
        return answer_result(
            f"{top['college']} is the leading college view: {int(top['partners'])} partner(s), {money(top['donations_made'])} donations, and {int(top['opportunities_created'])} opportunity record(s).",
            chart=college_summary(scored).set_index("college")[["partners"]].head(8),
        )

    return answer_result(
        "I can answer executive questions on top partners, cold partners, colleges with the most partners, donations, visits, event attendance, emails, and opportunities."
    )


def chat_module(df, rules):
    st.markdown("## Ask AI")
    st.write("Ask in plain English. The answer now starts with a direct executive sentence; charts or tables appear only when useful.")
    show_supporting = st.toggle("Show supporting chart/table when available", value=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    suggestions = st.columns(4)
    prompts = [
        "Which college has more partners?",
        "Which partners attend events most often?",
        "Who are the top donors?",
        "Which partners are cold?",
    ]
    selected_prompt = None
    for idx, prompt in enumerate(prompts):
        if suggestions[idx].button(prompt):
            selected_prompt = prompt

    question = st.chat_input("Ask a management question about partners")
    if selected_prompt:
        question = selected_prompt
    if question:
        st.session_state.chat_history.append((question, answer_question(question, df, rules)))

    for question_text, answer in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(question_text)
        with st.chat_message("assistant"):
            st.write(answer["text"])
            if show_supporting and answer.get("chart") is not None:
                st.bar_chart(answer["chart"])
            if show_supporting and answer.get("table") is not None:
                st.dataframe(answer["table"], use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon=":briefcase:", layout="wide")
    apply_style()

    st.markdown(
        """
        <div class="executive-band">
            <h1>Corporate Visits AI</h1>
            <p>Prestigious university partner intelligence for visits, events, giving, communications, and opportunity pipeline.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = clean_dataframe(load_data())
    rules = load_cold_rules()
    filtered = filter_data(df)

    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Module",
            ["Management Overview", "Partner CRM", "Upload and Export", "Cold Rules", "Ask AI"],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption(f"Database: {DATA_FILE}")
        if st.button("Reset to sample data"):
            save_data(sample_data())
            st.rerun()

    if page == "Management Overview":
        management_module(filtered, rules)
    elif page == "Partner CRM":
        editor_module(df, rules)
    elif page == "Upload and Export":
        upload_module(df, rules)
    elif page == "Cold Rules":
        rules_module(df, rules)
    elif page == "Ask AI":
        chat_module(filtered, rules)


if __name__ == "__main__":
    main()
