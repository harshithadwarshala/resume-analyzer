import streamlit as st
import db

st.set_page_config(page_title="Recruiter", page_icon="💼", layout="wide")

db.init_db()

st.title("💼 Recruiter Dashboard")
st.subheader("Post a new job")

title = st.text_input("Job title", placeholder="Python Developer")
description = st.text_area("Job description", height=180)

if st.button("Save job"):
    if not title.strip() or not description.strip():
        st.warning("Enter both job title and job description.")
    else:
        job_id = db.add_job(title.strip(), description.strip())
        st.success(f"Job saved. Job ID: {job_id}")

st.divider()
st.subheader("Posted jobs")

jobs = db.get_jobs()
if jobs:
    st.dataframe(
        [{"Job ID": j["job_id"], "Title": j["title"], "Posted": j["created_at"]} for j in jobs],
        hide_index=True,
    )
else:
    st.info("No jobs posted yet.")