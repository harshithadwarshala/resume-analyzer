import re
from io import BytesIO

import streamlit as st
from pypdf import PdfReader

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from xml.sax.saxutils import escape


# --------------------------------------------------
# 1. PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI-Based Resume Analyzer")

st.write(
    "Analyze resumes, identify skills, compare candidates "
    "and check job description matching."
)


# --------------------------------------------------
# 2. SKILLS DATABASE
# --------------------------------------------------

SKILLS = [
    "python", "java", "c++", "c#", "javascript",
    "sql", "mysql", "html", "css", "react",
    "node.js", "django", "flask", "streamlit",
    "machine learning", "deep learning",
    "data science", "artificial intelligence",
    "pandas", "numpy", "tensorflow", "pytorch",
    "power bi", "tableau", "excel",
    "data analysis", "data visualization",
    "git", "github", "aws", "azure",
    "docker", "linux", "communication",
    "problem solving", "teamwork",
    "leadership", "prompt engineering"
]


# --------------------------------------------------
# 3. IDENTIFY SKILLS
# --------------------------------------------------

def identify_skills(text):

    found_skills = []

    for skill in SKILLS:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(skill)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, text, re.IGNORECASE):

            found_skills.append(skill.title())

    return found_skills


# --------------------------------------------------
# 4. CANDIDATE INFORMATION EXTRACTION
# --------------------------------------------------

def extract_candidate_info(text):

    email = re.search(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        text
    )

    phone = re.search(
        r'(\+91[\s-]?)?[6-9]\d{9}',
        text
    )

    name = "Not identified"

    for line in text.splitlines()[:10]:

        line = line.strip()

        if (
            2 <= len(line.split()) <= 4
            and re.fullmatch(r"[A-Za-z ]+", line)
            and line.lower() not in [
                "resume",
                "curriculum vitae"
            ]
        ):

            name = line
            break

    education = []

    education_words = [
        "b.tech", "bachelor", "master",
        "degree", "university", "college",
        "b.sc", "m.sc", "m.tech",
        "diploma", "bca", "mca", "mba"
    ]

    for line in text.splitlines():

        if any(
            word in line.lower()
            for word in education_words
        ):

            education.append(line.strip())

    return {
        "Name": name,
        "Email": email.group() if email else "Not found",
        "Phone": phone.group() if phone else "Not found",
        "Education": education
    }


# --------------------------------------------------
# 5. PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_resume_text(pdf_file):

    pdf_file.seek(0)

    reader = PdfReader(pdf_file)

    if reader.is_encrypted:

        reader.decrypt("")

    text = ""

    for page in reader.pages:

        text += page.extract_text() or ""

    return text.strip()


# --------------------------------------------------
# 6. MATCH PERCENTAGE
# --------------------------------------------------

def calculate_match(matched, required):

    if not required:
        return 0

    return (
        len(matched) / len(required)
    ) * 100


# --------------------------------------------------
# 7. EDUCATION IDENTIFICATION
# --------------------------------------------------

def find_education(text):

    keywords = [
        "b.tech", "bachelor", "master",
        "degree", "university", "college",
        "b.sc", "m.sc", "m.tech",
        "diploma", "bca", "mca", "mba"
    ]

    results = []

    for line in text.splitlines():

        if any(
            word in line.lower()
            for word in keywords
        ):

            results.append(line.strip())

    return results


# --------------------------------------------------
# 8. EXPERIENCE IDENTIFICATION
# --------------------------------------------------

def find_experience(text):

    keywords = [
        "experience", "internship",
        "intern", "worked",
        "employment", "fresher"
    ]

    results = []

    for line in text.splitlines():

        if any(
            word in line.lower()
            for word in keywords
        ):

            results.append(line.strip())

    return results


# --------------------------------------------------
# 9. RESUME SUGGESTIONS
# --------------------------------------------------

def create_suggestions(
    missing_skills,
    education,
    experience,
    text
):

    suggestions = []

    if missing_skills:

        suggestions.append(
            "Improve these skills: "
            + ", ".join(missing_skills)
        )

    if not education:

        suggestions.append(
            "Add your education details."
        )

    if not experience:

        suggestions.append(
            "Add internship or project experience."
        )

    if not re.search(r"\bprojects?\b", text, re.I):

        suggestions.append(
            "Add a Projects section to your resume."
        )

    if not suggestions:

        suggestions.append(
            "Your resume looks good. "
            "Keep improving your skills."
        )

    return suggestions


# --------------------------------------------------
# 10. RESUME STRENGTHS
# --------------------------------------------------

def find_strengths(
    matched_skills,
    education,
    experience
):

    strengths = []

    if matched_skills:

        strengths.append(
            "Relevant skills identified successfully."
        )

    if education:

        strengths.append(
            "Education details identified."
        )

    if experience:

        strengths.append(
            "Experience details identified."
        )

    if not strengths:

        strengths.append(
            "Resume text extracted successfully."
        )

    return strengths


# --------------------------------------------------
# 11. CAREER RECOMMENDATIONS
# --------------------------------------------------

def career_recommendations(skills):

    skills = [s.lower() for s in skills]

    careers = []

    if any(
        s in skills
        for s in ["python", "machine learning", "data science"]
    ):

        careers.append("Python Developer")

    if any(
        s in skills
        for s in ["sql", "mysql", "power bi", "tableau"]
    ):

        careers.append("Data Analyst")

    if any(
        s in skills
        for s in ["html", "css", "javascript", "react"]
    ):

        careers.append("Frontend Developer")

    if any(
        s in skills
        for s in ["java", "python", "django", "flask"]
    ):

        careers.append("Software Developer")

    if not careers:

        careers.append("Entry Level Technology Role")

    return list(set(careers))


# --------------------------------------------------
# 12. ATS SCORE
# --------------------------------------------------

def calculate_ats_score(text, skills):

    score = 0

    if len(text.split()) >= 100:
        score += 20

    if "@" in text:
        score += 15

    if re.search(r"\beducation\b", text, re.I):
        score += 15

    if re.search(
        r"\b(experience|projects|internship)\b",
        text,
        re.I
    ):
        score += 15

    if skills:
        score += 35

    return min(score, 100)


# --------------------------------------------------
# 13. PDF REPORT GENERATION
# --------------------------------------------------

def generate_pdf_report(
    candidate,
    matched,
    missing,
    percentage,
    education,
    experience,
    suggestions,
    strengths,
    ats_score
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Resume Analysis Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 20))

    def add_section(title, content):

        story.append(
            Paragraph(
                escape(title),
                styles["Heading2"]
            )
        )

        if isinstance(content, list):

            if content:

                for item in content:

                    story.append(
                        Paragraph(
                            escape(str(item)),
                            styles["BodyText"]
                        )
                    )

            else:

                story.append(
                    Paragraph(
                        "Not identified",
                        styles["BodyText"]
                    )
                )

        else:

            story.append(
                Paragraph(
                    escape(str(content)),
                    styles["BodyText"]
                )
            )

        story.append(Spacer(1, 10))

    add_section("Candidate Name", candidate["Name"])
    add_section("Email", candidate["Email"])
    add_section("Phone", candidate["Phone"])

    add_section(
        "Match Percentage",
        f"{percentage:.2f}%"
    )

    add_section("Matched Skills", matched)
    add_section("Missing Skills", missing)
    add_section("Education", education)
    add_section("Experience", experience)
    add_section("Resume Strengths", strengths)
    add_section("Suggestions", suggestions)

    add_section(
        "ATS Compatibility Estimate",
        f"{ats_score}/100"
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# --------------------------------------------------
# 14. JOB DESCRIPTION
# --------------------------------------------------

st.divider()

st.subheader("1. Job Description")

job_description = st.text_area(
    "Paste Job Description",

    height=150,

    placeholder=(
        "We are looking for a Python Developer "
        "with knowledge of Python, Java, SQL, "
        "MySQL, HTML, CSS and Machine Learning."
    )
)


# --------------------------------------------------
# 15. SINGLE RESUME ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("2. Upload Resume")

uploaded_resume = st.file_uploader(
    "Upload Resume PDF",

    type=["pdf"],

    key="single_resume"
)


if uploaded_resume:

    try:

        resume_text = extract_resume_text(
            uploaded_resume
        )

        if not resume_text:

            st.error(
                "No readable text found in this PDF. "
                "It may be a scanned PDF."
            )

        else:

            st.success(
                "Resume uploaded successfully!"
            )

            # CANDIDATE DETAILS

            candidate = extract_candidate_info(
                resume_text
            )

            st.divider()

            st.subheader(
                "3. Candidate Information"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Name:**",
                    candidate["Name"]
                )

                st.write(
                    "**Email:**",
                    candidate["Email"]
                )

            with col2:

                st.write(
                    "**Phone:**",
                    candidate["Phone"]
                )

            st.write("**Education:**")

            if candidate["Education"]:

                for item in candidate["Education"]:

                    st.write("- " + item)

            else:

                st.write("Not identified")

            # SKILLS

            resume_skills = identify_skills(
                resume_text
            )

            st.divider()

            st.subheader(
                "4. Identified Skills"
            )

            st.write(
                ", ".join(resume_skills)
                if resume_skills
                else "No skills identified."
            )

            # MATCHING

            st.divider()

            st.subheader(
                "5. Job Description Matching"
            )

            required_skills = identify_skills(
                job_description
            )

            matched_skills = [
                skill
                for skill in required_skills
                if skill in resume_skills
            ]

            missing_skills = [
                skill
                for skill in required_skills
                if skill not in resume_skills
            ]

            match_percentage = calculate_match(
                matched_skills,
                required_skills
            )

            if not job_description.strip():

                st.warning(
                    "Please enter a job description."
                )

            elif not required_skills:

                st.warning(
                    "No predefined skills found in job description."
                )

            else:

                st.write("**Matched Skills:**")

                st.write(
                    ", ".join(matched_skills)
                    if matched_skills
                    else "None"
                )

                st.write("**Missing Skills:**")

                st.write(
                    ", ".join(missing_skills)
                    if missing_skills
                    else "None"
                )

                st.metric(
                    "Resume Match Percentage",
                    f"{match_percentage:.2f}%"
                )

                st.progress(
                    int(match_percentage)
                )

                if match_percentage >= 70:

                    st.success(
                        "Your resume has a good match "
                        "with the job description."
                    )

                elif match_percentage >= 40:

                    st.warning(
                        "Your resume has a moderate match "
                        "with the job description."
                    )

                else:

                    st.error(
                        "Your resume has a low match "
                        "with the job description."
                    )

            # EDUCATION

            st.divider()

            st.subheader(
                "6. Education Identification"
            )

            education = find_education(
                resume_text
            )

            if education:

                for item in education:

                    st.write("- " + item)

            else:

                st.write("No education details found.")

            # EXPERIENCE

            st.divider()

            st.subheader(
                "7. Experience / Internship"
            )

            experience = find_experience(
                resume_text
            )

            if experience:

                for item in experience:

                    st.write("- " + item)

            else:

                st.write("No experience details found.")

            # STRENGTHS

            st.divider()

            st.subheader(
                "8. Resume Strengths"
            )

            strengths = find_strengths(
                matched_skills,
                education,
                experience
            )

            for item in strengths:

                st.write("✅ " + item)

            # SUGGESTIONS

            st.divider()

            st.subheader(
                "9. Resume Improvement Suggestions"
            )

            suggestions = create_suggestions(
                missing_skills,
                education,
                experience,
                resume_text
            )

            for item in suggestions:

                st.write("💡 " + item)

            # CAREER

            st.divider()

            st.subheader(
                "10. Career Recommendations"
            )

            careers = career_recommendations(
                resume_skills
            )

            for career in careers:

                st.write("🎯 " + career)

            # ATS

            st.divider()

            st.subheader(
                "11. ATS Compatibility Estimate"
            )

            ats_score = calculate_ats_score(
                resume_text,
                resume_skills
            )

            st.metric(
                "ATS Score",
                f"{ats_score}/100"
            )

            st.progress(ats_score)

            st.caption(
                "This is a basic keyword and structure estimate, "
                "not a score from a commercial ATS platform."
            )

            # DASHBOARD

            st.divider()

            st.subheader(
                "12. Resume Analysis Dashboard"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Skills Found",
                len(resume_skills)
            )

            col2.metric(
                "Matched Skills",
                len(matched_skills)
            )

            col3.metric(
                "Missing Skills",
                len(missing_skills)
            )

            st.write(
                "### Skill Match Overview"
            )

            st.bar_chart({
                "Skills": {
                    "Matched": len(matched_skills),
                    "Missing": len(missing_skills)
                }
            })

            # PDF DOWNLOAD

            st.divider()

            st.subheader(
                "13. Download Resume Report"
            )

            pdf_report = generate_pdf_report(
                candidate,
                matched_skills,
                missing_skills,
                match_percentage,
                education,
                experience,
                suggestions,
                strengths,
                ats_score
            )

            st.download_button(
                "📥 Download PDF Report",

                data=pdf_report,

                file_name="Resume_Analysis_Report.pdf",

                mime="application/pdf"
            )

    except Exception as error:

        st.error(
            f"Unable to process resume: {error}"
        )


# --------------------------------------------------
# 16. MULTIPLE RESUME COMPARISON
# --------------------------------------------------

st.divider()

st.subheader(
    "14. Multiple Resume Comparison"
)

st.write(
    "Upload 2–4 candidate resumes and compare "
    "them against the same job description."
)

multiple_resumes = st.file_uploader(
    "Upload Candidate Resumes",

    type=["pdf"],

    accept_multiple_files=True,

    key="multiple_resumes"
)


if multiple_resumes:

    if len(multiple_resumes) < 2:

        st.warning(
            "Please upload at least 2 resumes."
        )

    elif len(multiple_resumes) > 4:

        st.warning(
            "Maximum 4 resumes allowed."
        )

    elif not job_description.strip():

        st.warning(
            "Please enter a job description."
        )

    else:

        comparison_required = identify_skills(
            job_description
        )

        if not comparison_required:

            st.warning(
                "No skills found in job description."
            )

        else:

            comparison_results = []

            for resume_file in multiple_resumes:

                try:

                    candidate_text = extract_resume_text(
                        resume_file
                    )

                    if not candidate_text:
                        st.warning(
                            f"No readable text found in "
                            f"{resume_file.name}."
                        )

                        continue

                    candidate_skills = identify_skills(
                        candidate_text
                    )

                    candidate_info = extract_candidate_info(
                        candidate_text
                    )

                    matched = [
                        skill
                        for skill in comparison_required
                        if skill in candidate_skills
                    ]

                    missing = [
                        skill
                        for skill in comparison_required
                        if skill not in candidate_skills
                    ]

                    percentage = calculate_match(
                        matched,
                        comparison_required
                    )

                    comparison_results.append({

                        "Resume": resume_file.name,

                        "Candidate": candidate_info["Name"],

                        "Match Percentage": round(
                            percentage,
                            2
                        ),

                        "Matched Skills": (
                            ", ".join(matched)
                            if matched else "None"
                        ),

                        "Missing Skills": (
                            ", ".join(missing)
                            if missing else "None"
                        )

                    })

                except Exception as error:

                    st.error(
                        f"Error processing {resume_file.name}: {error}"
                    )

            if comparison_results:

                comparison_results.sort(
                    key=lambda x: x["Match Percentage"],
                    reverse=True
                )

                st.write(
                    "### Candidate Comparison Table"
                )

                st.dataframe(
                    comparison_results,
                    use_container_width=True,
                    hide_index=True
                )

                st.write(
                    "### Candidate Match Percentage Chart"
                )

                chart_data = {
                    item["Candidate"]
                    if item["Candidate"] != "Not identified"
                    else item["Resume"]:
                    item["Match Percentage"]
                    for item in comparison_results
                }

                st.bar_chart(chart_data)

                best_candidate = comparison_results[0]

                st.write(
                    "### Best Matching Candidate"
                )

                st.success(
                    "🏆 Best Matching Resume: "
                    + best_candidate["Resume"]
                )

                st.metric(
                    "Highest Match Score",
                    f"{best_candidate['Match Percentage']:.2f}%"
                )

                st.write(
                    "### Candidate Ranking"
                )

                for rank, candidate in enumerate(
                    comparison_results,
                    start=1
                ):

                    st.write(
                        f"**{rank}. {candidate['Candidate']}** "
                        f"— {candidate['Match Percentage']:.2f}%"
                    )

            else:

                st.warning(
                    "No readable resumes available for comparison."
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI-Based Resume Analyzer | Python | Streamlit | "
    "PDF Processing | ATS Keyword Analysis"
)