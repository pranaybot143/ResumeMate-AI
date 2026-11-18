
import streamlit as st

from core.report_generator import generate_report


# =====================================================
# 1. LOAD PAGE STYLING
# =====================================================

with open("assets/css/reports.css", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 2. PAGE HEADER
# =====================================================

st.title("Analysis Reports")

st.markdown(
    '<p class="reports-subtitle">'
    'Your resume analysis, organised into a downloadable report.'
    '</p>',
    unsafe_allow_html=True
)

st.caption(
    "Review your analysis summary and download the complete PDF report."
)


# =====================================================
# 3. RETRIEVE ANALYSIS DATA
# =====================================================

data = st.session_state.get("analysis_data", {})

if not data:
    st.warning("No analysis results available. Please analyse a resume first.")
    st.stop()

resume_filename = st.session_state.get(
    "resume_filename",
    "Resume"
)


# =====================================================
# 4. REPORT OVERVIEW
# =====================================================

st.subheader("Report Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Semantic Match Score",
        f"{data.get('score', 0)}%"
    )

with col2:
    coverage = data.get("skill_coverage")

    st.metric(
        "Skill Coverage",
        f"{coverage}%" if coverage is not None else "N/A"
    )


# =====================================================
# 5. REPORT CONTENTS
# =====================================================

st.divider()

st.subheader("What's Included")

st.caption(
    "Your PDF report brings together the key findings from your latest analysis."
)

report_sections = [
    ("01", "Resume Analysis Score", "Semantic similarity between your resume and the job description."),
    ("02", "Skill Coverage", "Percentage of required skills detected in your resume."),
    ("03", "Skill Comparison", "Matching and missing technical skills."),
    ("04", "AI Feedback Summary", "Personalised feedback and improvement suggestions."),
    ("05", "Skill Development", "Recommendations for developing missing skills."),
    ("06", "Resume Evidence", "Selected evidence supporting detected technical skills.")
]

for number, title, description in report_sections:

    st.markdown(
        f"""
        <div class="report-content-item">
            <span class="report-content-number">{number}</span>
            <div class="report-content-text">
                <strong>{title}</strong>
                <p>{description}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# 6. GENERATE PDF REPORT
# =====================================================

st.divider()

st.subheader("Download Your Report")

try:

    pdf_report = generate_report(
        data,
        resume_filename
    )

    st.markdown(
        """
        <div class="download-panel">
            <div class="download-panel-heading">
                PDF Analysis Report
            </div>
            <p>
                Your latest resume analysis has been compiled into a
                downloadable PDF document.
            </p>
            <div class="download-panel-meta">
                FORMAT: PDF &nbsp; · &nbsp; GENERATED FROM LATEST ANALYSIS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.download_button(
        label="Download Analysis Report",
        data=pdf_report,
        file_name="ResumeMate_Analysis_Report.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )

    st.markdown(
        '<p class="download-note">'
        'Your report is generated using the results of your latest analysis.'
        '</p>',
        unsafe_allow_html=True
    )

except Exception as error:

    st.error(f"Unable to generate the PDF report: {error}")
