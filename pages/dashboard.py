import html
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# 1. LOAD DASHBOARD STYLING
# =====================================================

with open("assets/css/dashboard.css", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 2. DASHBOARD HEADER
# =====================================================

st.title("Analysis Dashboard")

st.caption(
    f"Analysis results for "
    f"{st.session_state.get('resume_filename', 'Resume')}"
)


# =====================================================
# 3. RETRIEVE ANALYSIS DATA
# =====================================================

data = st.session_state.get("analysis_data", {})

if not data:
    st.warning("No analysis results available. Please analyse a resume first.")
    st.stop()

score = data.get("score", 0)
coverage = data.get("skill_coverage")

matching_skills = data.get("matching_skills", [])
missing_skills = data.get("missing_skills", [])

matched_count = len(matching_skills)
missing_count = len(missing_skills)
total_count = matched_count + missing_count


# =====================================================
# 4. OVERALL SCORE CARDS
# =====================================================

st.subheader("Overall Analysis")

col1, col2 = st.columns(2)

with col1:
    st.metric("Semantic Match Score", f"{score}%")

with col2:
    st.metric(
        "Skill Coverage",
        f"{coverage}%" if coverage is not None else "N/A"
    )

st.caption(
    "Semantic similarity and skill coverage are separate indicators, "
    "not hiring probabilities."
)

st.divider()


# =====================================================
# 5. SKILL VISUALISATIONS
# =====================================================

st.subheader("Skill Analysis")

chart_col1, chart_col2 = st.columns(2)


# -----------------------------------------------------
# DONUT CHART
# -----------------------------------------------------

with chart_col1:

    st.markdown("**Skill Coverage Distribution**")

    if total_count > 0:

        donut = go.Figure(
            data=[
                go.Pie(
                    labels=["Matched Skills", "Missing Skills"],
                    values=[matched_count, missing_count],
                    hole=0.72,
                    sort=False,
                    marker=dict(
                        colors=["#3B82F6", "#475569"],
                        line=dict(color="#1E293B", width=3)
                    ),
                    textinfo="percent",
                    textfont=dict(
                        family="Manrope",
                        size=13,
                        color="#F8FAFC"
                    ),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Skills: %{value}<br>"
                        "Share: %{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )

        donut.update_layout(
            template="plotly_dark",
            height=400,
            autosize=True,
            margin=dict(t=20, b=65, l=15, r=15),
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
            font=dict(family="Manrope", color="#CBD5E1"),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.12,
                xanchor="center",
                x=0.5,
                font=dict(size=11)
            ),
            annotations=[
                dict(
                    text=f"<b>{matched_count}/{total_count}</b>",
                    x=0.5,
                    y=0.5,
                    font=dict(
                        size=25,
                        color="#F8FAFC",
                        family="Manrope"
                    ),
                    showarrow=False
                )
            ]
        )

        st.plotly_chart(
            donut,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )

    else:
        st.info("No recognised skills available.")


# -----------------------------------------------------
# HORIZONTAL BAR CHART
# -----------------------------------------------------

with chart_col2:

    st.markdown("**Matching vs Missing Skills**")

    if total_count > 0:

        bar_chart = go.Figure()

        bar_chart.add_trace(
            go.Bar(
                y=["Matching Skills", "Missing Skills"],
                x=[matched_count, missing_count],
                orientation="h",
                marker=dict(
                    color=["#3B82F6", "#64748B"],
                    line=dict(width=0)
                ),
                text=[matched_count, missing_count],
                textposition="outside",
                cliponaxis=False,
                textfont=dict(
                    family="Manrope",
                    color="#F8FAFC",
                    size=14
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Number of skills: %{x}"
                    "<extra></extra>"
                )
            )
        )

        bar_chart.update_layout(
            template="plotly_dark",
            height=400,
            autosize=True,
            margin=dict(t=20, b=65, l=15, r=45),
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
            font=dict(family="Manrope", color="#CBD5E1"),
            showlegend=False,
            xaxis=dict(
                title="Number of Skills",
                showgrid=True,
                gridcolor="#334155",
                zeroline=False,
                rangemode="tozero"
            ),
            yaxis=dict(
                showgrid=False,
                autorange="reversed"
            )
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )

    else:
        st.info("No skill data available.")


st.divider()


# =====================================================
# 6. MATCHING AND MISSING SKILLS
# =====================================================

st.subheader("Required Skills Comparison")


def display_skill_tags(skills, css_class):
    """Display detected skills as visual tags."""

    if not skills:
        st.caption("No skills to display.")
        return

    tags = "".join(
        f'<span class="skill-tag {css_class}">'
        f'{html.escape(str(skill))}</span>'
        for skill in skills
    )

    st.markdown(
        f'<div class="skill-tag-container">{tags}</div>',
        unsafe_allow_html=True
    )


col1, col2 = st.columns(2)

with col1:
    st.markdown("**Matching Skills**")
    st.caption(f"{matched_count} skills detected in your resume")
    display_skill_tags(matching_skills, "matched")

with col2:
    st.markdown("**Missing Skills**")
    st.caption(f"{missing_count} skills not detected in your resume")
    display_skill_tags(missing_skills, "missing")


# =====================================================
# 7. DISCLAIMER
# =====================================================

st.divider()

st.caption(
    "ResumeMate AI provides automated resume analysis and career guidance. "
    "Results should not be interpreted as guaranteed hiring outcomes."
)
