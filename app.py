import streamlit as st


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ResumeMate AI",
    page_icon="📄",
    layout="wide"
)


# =====================================================
# 2. LOAD GLOBAL STYLING
# =====================================================

with open("assets/css/global.css", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 3. INITIALIZE SESSION STATE
# =====================================================

st.session_state.setdefault("resume_text", "")
st.session_state.setdefault("resume_filename", "")
st.session_state.setdefault("analysis_data", {})
st.session_state.setdefault("analysis_complete", False)


# =====================================================
# 4. REGISTER ALL APPLICATION PAGES
# =====================================================

analysis_complete = st.session_state.analysis_complete

upload_page = st.Page(
    "pages/upload.py",
    title="New Analysis",
    icon=":material/upload_file:",
    default=not analysis_complete,
    visibility="visible"
)

dashboard_page = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=analysis_complete,
    visibility="visible" if analysis_complete else "hidden"
)

evidence_page = st.Page(
    "pages/evidence.py",
    title="Resume Evidence",
    icon=":material/search:",
    visibility="visible" if analysis_complete else "hidden"
)

insights_page = st.Page(
    "pages/ai_insights.py",
    title="AI Insights",
    icon=":material/psychology:",
    visibility="visible" if analysis_complete else "hidden"
)

reports_page = st.Page(
    "pages/reports.py",
    title="Reports",
    icon=":material/description:",
    visibility="visible" if analysis_complete else "hidden"
)


# =====================================================
# 5. NAVIGATION
# =====================================================

pages = [
    dashboard_page,
    evidence_page,
    insights_page,
    reports_page,
    upload_page
]

navigation = st.navigation(pages)

navigation.run()
