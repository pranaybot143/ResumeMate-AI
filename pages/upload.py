import re
import streamlit as st

from pypdf import PdfReader

from core.ai_analyzer import calculate_similarity
from core.skill_extractor import extract_skills, extract_skill_evidence
from core.recommendation_engine import generate_recommendations


# =====================================================
# 1. LOAD UPLOAD PAGE STYLING
# =====================================================

with open("assets/css/upload.css", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 2. SESSION STATE INITIALIZATION
# =====================================================

st.session_state.setdefault("resume_text", "")
st.session_state.setdefault("resume_filename", "")
st.session_state.setdefault("analysis_data", {})
st.session_state.setdefault("analysis_complete", False)


# =====================================================
# 3. PAGE HEADER
# =====================================================

st.title("ResumeMate AI")

st.markdown(
    '<p class="upload-subtitle">'
    'AI-Powered Resume Analysis and Job Matching'
    '</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="upload-description">'
    'Evaluate your resume against a job description, identify skill gaps, '
    'and receive personalised recommendations.'
    '</p>',
    unsafe_allow_html=True
)


# =====================================================
# 4. RESUME UPLOAD
# =====================================================

with st.container(border=True):

    st.subheader("Upload Your Resume")

    st.caption(
        "Upload your resume in PDF format to begin the analysis."
    )

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf"],
        help="PDF only · Maximum size: 5 MB · Maximum length: 5 pages",
        key="resume_uploader"
    )

    if uploaded_file is not None:

        upload_signature = f"{uploaded_file.name}:{uploaded_file.size}"

        if st.session_state.get("upload_signature") != upload_signature:

            st.session_state.resume_text = ""
            st.session_state.resume_filename = ""
            st.session_state.analysis_data = {}
            st.session_state.analysis_complete = False
            st.session_state.upload_signature = upload_signature

            try:

                if uploaded_file.size > 5 * 1024 * 1024:

                    st.error("PDF size must not exceed 5 MB.")

                else:

                    pdf_reader = PdfReader(uploaded_file)

                    # Password protection validation
                    if pdf_reader.is_encrypted:

                        try:
                            result = pdf_reader.decrypt("")

                            if not result:
                                st.error(
                                    "Password-protected PDFs are not supported."
                                )
                                st.stop()

                        except Exception:
                            st.error("Unable to open this protected PDF.")
                            st.stop()

                    # Page count validation
                    if len(pdf_reader.pages) > 5:

                        st.error(
                            "Resume must not contain more than 5 pages."
                        )

                    elif len(pdf_reader.pages) == 0:

                        st.error("The uploaded PDF is empty.")

                    else:

                        extracted_text = ""

                        for page in pdf_reader.pages:
                            extracted_text += (
                                page.extract_text() or ""
                            ) + "\n"

                        if extracted_text.strip():

                            st.session_state.resume_text = extracted_text
                            st.session_state.resume_filename = uploaded_file.name

                            st.success(
                                "Resume uploaded and validated successfully!"
                            )

                        else:

                            st.error(
                                "No readable text found. This may be a scanned "
                                "PDF. Image-based resumes are not supported yet."
                            )

            except Exception as error:

                st.session_state.resume_text = ""
                st.session_state.resume_filename = ""
                st.error(f"Unable to process this PDF: {error}")

    # Resume status and preview
    if st.session_state.resume_text:

        st.markdown(
            f'<div class="resume-status">'
            f'<span class="status-indicator"></span>'
            f'<span><strong>Resume ready</strong><br>'
            f'{st.session_state.resume_filename}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        with st.expander("Preview extracted resume text"):

            st.text_area(
                "Extracted Content",
                st.session_state.resume_text,
                height=180,
                disabled=True,
                key="resume_preview"
            )

    elif uploaded_file is None and st.session_state.resume_filename:

        st.info(
            f"Previously uploaded resume: "
            f"{st.session_state.resume_filename}"
        )


# =====================================================
# 5. JOB DESCRIPTION
# =====================================================

with st.container(border=True):

    st.subheader("Job Description")

    st.caption(
        "Paste the job description you want to compare your resume against."
    )

    job_description = st.text_area(
        "Job description",
        height=220,
        placeholder=(
            "Paste the job description here...\n\n"
            "Include the required technical skills, qualifications, "
            "responsibilities and experience."
        ),
        key="job_description_input"
    )


# =====================================================
# 6. PRIVACY NOTICE AND CONSENT
# =====================================================

with st.container(border=True):

    st.subheader("Privacy and Consent")

    st.markdown(
        """
        <div class="privacy-notice">
            <strong>AI processing notice</strong>
            <p>
                To generate personalised feedback, ResumeMate AI sends your
                extracted resume text and job description to Google's Gemini
                API. Avoid uploading documents containing information you
                do not want processed by this external service.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    consent = st.checkbox(
        "I understand that my resume text and job description will be sent "
        "to Google Gemini for AI-powered feedback.",
        key="ai_consent"
    )


# =====================================================
# 7. ANALYSE RESUME
# =====================================================

st.markdown('<div class="analyse-section">', unsafe_allow_html=True)

analyse_clicked = st.button(
    "Analyse Resume",
    type="primary",
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


if analyse_clicked:

    resume_text = st.session_state.resume_text

    if not resume_text.strip():

        st.error("Please upload a valid resume first.")

    elif not job_description.strip():

        st.error("Please enter a job description.")

    elif not consent:

        st.error(
            "Please confirm the AI privacy notice before proceeding."
        )

    else:

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z+#.]*\b",
            job_description
        )

        if len(job_description.strip()) < 50:

            st.error("Job description is too short.")

        elif len(words) < 10:

            st.error("Please enter a meaningful job description.")

        elif not extract_skills(job_description):

            st.error(
                "No recognised technical skills found. "
                "Please enter a relevant technical job description."
            )

        else:

            try:

                with st.spinner(
                    "Analysing your resume and generating AI feedback..."
                ):

                    # 1. Semantic similarity
                    score = calculate_similarity(
                        resume_text,
                        job_description
                    )

                    # 2. Extract skills and resume evidence
                    resume_skills = extract_skills(resume_text)

                    resume_skill_evidence = extract_skill_evidence(
                        resume_text
                    )

                    job_skills = extract_skills(job_description)

                    # 3. Compare skills
                    matching_skills = [
                        skill for skill in job_skills
                        if skill in resume_skills
                    ]

                    missing_skills = [
                        skill for skill in job_skills
                        if skill not in resume_skills
                    ]

                    # 4. Calculate skill coverage
                    skill_coverage = (
                        len(matching_skills) / len(job_skills) * 100
                        if job_skills else None
                    )

                    # 5. Generate AI feedback
                    ai_result = generate_recommendations(
                        resume_text=resume_text,
                        job_description=job_description,
                        matching_skills=matching_skills,
                        missing_skills=missing_skills,
                        resume_skill_evidence=resume_skill_evidence
                    )

                # Store analysis results
                st.session_state.analysis_data = {
                    "score": score,
                    "skill_coverage": (
                        round(skill_coverage, 2)
                        if skill_coverage is not None
                        else None
                    ),
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills,
                    "resume_skill_evidence": resume_skill_evidence,
                    "total_skills": len(job_skills),
                    "recommendations": ai_result["recommendations"],
                    "ai_feedback": ai_result["ai_feedback"],
                    "recommendation_source": ai_result["source"],
                    "recommendation_warning": ai_result.get("warning", "")
                }

                st.session_state.analysis_complete = True

                st.switch_page("pages/dashboard.py")

            except Exception as error:

                st.error(f"Analysis failed: {error}")
