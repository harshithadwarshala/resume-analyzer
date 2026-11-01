import streamlit as st
import pandas as pd
import db
import auth

st.set_page_config(
    page_title="Recruiter",
    page_icon="💼",
    layout="wide"
)

# Recruiter Authentication
auth.require_login()

# Initialize Database
db.init_db()

st.title("💼 Recruiter Dashboard")
st.write("Manage job postings and view candidates.")

st.divider()

# POST NEW JOB
st.subheader("📝 Post a New Job")

with st.form("job_form"):
    job_title = st.text_input("Job Title")

    job_description = st.text_area(
        "Job Description",
        height=180,
        placeholder="Enter job requirements, skills and responsibilities..."
    )

    submitted = st.form_submit_button(
        "➕ Post Job",
        use_container_width=True
    )

    if submitted:
        if job_title.strip() and job_description.strip():
            job_id = db.add_job(
                job_title.strip(),
                job_description.strip()
            )

            st.success(
                f"Job posted successfully! Job ID: {job_id}"
            )
            st.rerun()
        else:
            st.warning("Please enter Job Title and Job Description.")

st.divider()

# DISPLAY POSTED JOBS
st.subheader("📋 Posted Jobs")

jobs = db.get_jobs()

if jobs:

    for job in jobs:
        with st.expander(
            f"{job['job_id']} - {job['title']}"
        ):
            st.write("**Job Description:**")
            st.write(job["description"])

            st.caption(
                f"Created At: {job['created_at']}"
            )

    st.divider()

    # VIEW APPLICANTS
    st.subheader("👥 Candidate Applications")

    job_options = {
        f"{job['job_id']} - {job['title']}": job["job_id"]
        for job in jobs
    }

    selected_job = st.selectbox(
        "Select Job",
        list(job_options.keys())
    )

    job_id = job_options[selected_job]

    applications = db.get_applications(job_id)

    if applications:

        st.success(
            f"Total Applicants: {len(applications)}"
        )

        df = pd.DataFrame(applications)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # VIEW RESUME
        st.subheader("📄 View Candidate Resume")

        resume_options = {
            f"{row['name']} - {row['resume_id']}":
            row["resume_id"]
            for row in applications
        }

        selected_resume = st.selectbox(
            "Select Candidate",
            list(resume_options.keys())
        )

        resume_id = resume_options[selected_resume]

        resume_text = db.get_resume_text(resume_id)

        st.text_area(
            "Resume Details",
            resume_text,
            height=300
        )

    else:
        st.info("No candidates have applied for this job yet.")

else:
    st.info("No jobs posted yet. Post your first job above!")