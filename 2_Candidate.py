import streamlit as st
import db
from utils import extract_text

st.set_page_config(page_title="Candidate", page_icon="🧑‍💻", layout="wide")

db.init_db()

st.title("🧑‍💻 Apply for a Job")

jobs = db.get_jobs()
if not jobs:
    st.info("No jobs available yet.")
    st.stop()

options = {f'{j["job_id"]} - {j["title"]}': j["job_id"] for j in jobs}
choice = st.selectbox("Select job", list(options.keys()))
job = db.get_job(options[choice])

name = st.text_input("Full name")
email = st.text_input("Email")
phone = st.text_input("Phone")
resume = st.file_uploader("Upload resume (PDF)", type=["pdf"])

if st.button("Apply"):
    if not (name.strip() and email.strip() and resume):
        st.warning("Enter name, email and upload resume.")
    else:
        resume_text = extract_text(resume)
        if not resume_text.strip():
            st.error("Could not read text from this PDF (scanned PDF ayyundochu).")
            st.stop()

        # Simple skill matching
        skills = ["python", "sql", "streamlit", "flask", "html", "css", "git",
                  "github", "pandas", "numpy", "machine learning", "oop",
                  "mysql", "sqlite", "internship", "project"]
        jd = job["description"].lower()
        rt = resume_text.lower()
        jd_skills = [s for s in skills if s in jd]
        matched = [s for s in jd_skills if s in rt]
        missing = [s for s in jd_skills if s not in rt]
        match = round(len(matched) / len(jd_skills) * 100, 1) if jd_skills else 0.0
        ats = int(match)

        cand_id, res_id = db.add_application(
            job["job_id"], name.strip(), email.strip(), phone.strip(),
            resume_text, match, ats, matched, missing
        )

        st.success("Applied successfully!")
        st.write(f"**Candidate ID:** {cand_id}")
        st.write(f"**Resume ID:** {res_id}")
        st.write(f"**Job:** {choice}")
        st.metric("Match %", f"{match}%")
        st.write("✅ Matched skills:", ", ".join(matched) or "None")
        st.write("❌ Missing skills:", ", ".join(missing) or "None")