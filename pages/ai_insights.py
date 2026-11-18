
import html
import streamlit as st


# =====================================================
# 1. LOAD PAGE STYLING
# =====================================================

with open("assets/css/insights.css", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 2. PAGE HEADER
# =====================================================

st.title("AI Insights")

st.markdown(
    '<p class="insights-subtitle">'
    'Personalised feedback and recommendations'
    '</p>',
    unsafe_allow_html=True
)

st.caption(
    "Actionable guidance based on your resume and the selected job description."
)


# =====================================================
# 3. RETRIEVE ANALYSIS DATA
# =====================================================

data = st.session_state.get("analysis_data", {})

if not data:
    st.warning("No analysis results available. Please analyse a resume first.")
    st.stop()

feedback = data.get("ai_feedback", {})
recommendations = data.get("recommendations", [])

source = data.get("recommendation_source", "fallback")
warning = data.get("recommendation_warning", "")


# =====================================================
# 4. AI GENERATION STATUS
# =====================================================

if source == "gemini":

    st.markdown(
        """
        <div class="ai-status-card ai-status-success">
            <span class="ai-status-dot"></span>
            <div>
                <strong>AI-generated feedback</strong>
                <p>Personalised recommendations generated using Google Gemini.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div class="ai-status-card ai-status-fallback">
            <span class="ai-status-dot"></span>
            <div>
                <strong>Fallback recommendations</strong>
                <p>AI-generated feedback is unavailable. General recommendations are being displayed instead.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if warning:
    st.warning(warning)


# =====================================================
# 5. OVERALL RESUME FEEDBACK
# =====================================================

st.subheader("Overall Resume Feedback")

overall_feedback = feedback.get("overall_feedback", "")

with st.container(border=True):

    if overall_feedback:

        st.markdown(
            f'<div class="overall-feedback">'
            f'{html.escape(str(overall_feedback))}'
            f'</div>',
            unsafe_allow_html=True
        )

    else:
        st.info("No overall feedback is available.")


# =====================================================
# 6. PERSONALISED FEEDBACK SECTIONS
# =====================================================

st.divider()

st.subheader("Personalised Feedback")

st.caption(
    "Explore specific areas where your resume can be strengthened."
)

feedback_sections = [
    ("01", "Strengths", "strengths"),
    ("02", "Areas to Improve", "improvement_areas"),
    ("03", "Learning Roadmap", "learning_roadmap"),
    ("04", "Suggested Projects", "project_suggestions"),
    ("05", "Resume Improvement Tips", "resume_tips")
]

available_sections = [
    (number, title, key, feedback.get(key, []))
    for number, title, key in feedback_sections
    if feedback.get(key)
]

if available_sections:

    for number, title, key, items in available_sections:

        with st.expander(
            f"{number}   {title}   ·   {len(items)} item(s)",
            expanded=False
        ):

            for index, item in enumerate(items, start=1):

                st.markdown(
                    f"""
                    <div class="feedback-item">
                        <span class="feedback-item-number">{index:02}</span>
                        <div class="feedback-item-content">
                            {html.escape(str(item))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

else:

    st.info("No personalised feedback sections are available.")


# =====================================================
# 7. SKILL DEVELOPMENT RECOMMENDATIONS
# =====================================================

st.divider()

st.subheader("Skill Development Recommendations")

st.caption(
    "Suggested ways to develop technical skills that were not detected in your resume."
)

if recommendations:

    recommendation_columns = st.columns(2)

    for index, item in enumerate(recommendations):

        skill = item.get("skill", "Unknown Skill")
        recommendation = item.get("recommendation", "")

        with recommendation_columns[index % 2]:

            with st.container(border=True):

                st.markdown(
                    f'<div class="recommendation-label">'
                    f'SKILL {index + 1:02}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="recommendation-skill">'
                    f'{html.escape(str(skill))}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="recommendation-description">'
                    f'{html.escape(str(recommendation))}'
                    f'</div>',
                    unsafe_allow_html=True
                )

else:

    st.success(
        "No missing skills were identified from our current skill vocabulary."
    )


# =====================================================
# 8. DISCLAIMER
# =====================================================

st.divider()

st.caption(
    "AI-generated feedback is intended as career guidance. "
    "Review recommendations critically and verify important information."
)
