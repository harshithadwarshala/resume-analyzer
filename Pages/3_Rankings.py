import streamlit as st
import db

st.set_page_config(page_title="Rankings", page_icon="🏆", layout="wide")

db.init_db()

st.title("🏆 Candidate Rankings")

jobs = db.get_jobs()
if not jobs:
    st.info("No jobs posted yet.")
    st.stop()

options = {f'{j["job_id"]} - {j["title"]}': j["job_id"] for j in jobs}
choice = st.selectbox("Select job", list(options.keys()))

apps = db.get_applications(options[choice])

if not apps:
    st.info("No applications for this job yet.")
else:

    min_score = st.slider("Minimum match %", 0, 100, 0)
    apps = [a for a in apps if a["match_percentage"] >= min_score]

    st.write(f"**Showing applicants:** {len(apps)}")

    rows = [
        {
            "Rank": i + 1,
            "Candidate ID": a["candidate_id"],
            "Resume ID": a["resume_id"],
            "Name": a["name"],
            "Email": a["email"],
            "Match %": a["match_percentage"],
            "Matched": a["matched_skills"],
            "Missing": a["missing_skills"],
        }
        for i, a in enumerate(apps)
    ]

    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")

        import pandas as pd
        csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "rankings.csv", "text/csv")

        st.divider()
        st.subheader("View resume")
        pick = st.selectbox("Select Resume ID", [r["Resume ID"] for r in rows])
        st.text_area("Resume text", db.get_resume_text(pick), height=300)
    else:
        st.info("No candidates above this score.")
