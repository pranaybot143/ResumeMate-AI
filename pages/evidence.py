import html
import streamlit as st
import plotly.graph_objects as go


# =====================================================
# 1. LOAD PAGE STYLING
# =====================================================

with open("assets/css/evidence.css", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# 2. PAGE HEADER
# =====================================================

st.title("Resume Evidence")

st.markdown(
    '<p class="evidence-subtitle">'
    'Understand how your technical skills appear in your resume.'
    '</p>',
    unsafe_allow_html=True
)

st.caption(
    "Review detected skills, their resume sections and the text supporting each detection."
)


# =====================================================
# 3. RETRIEVE ANALYSIS DATA
# =====================================================

data = st.session_state.get("analysis_data", {})

if not data:
    st.warning("No analysis results available. Please analyse a resume first.")
    st.stop()

evidence_items = data.get("resume_skill_evidence", [])

total_detected = len(evidence_items)

listed_count = sum(
    1 for item in evidence_items
    if any(
        evidence.get("evidence_type") == "listed"
        for evidence in item.get("evidence", [])
    )
)

demonstrated_count = sum(
    1 for item in evidence_items
    if any(
        evidence.get("evidence_type") == "demonstrated"
        for evidence in item.get("evidence", [])
    )
)

professional_count = sum(
    1 for item in evidence_items
    if any(
        evidence.get("evidence_type") == "professional_experience"
        for evidence in item.get("evidence", [])
    )
)


# =====================================================
# 4. SUMMARY CARDS
# =====================================================

st.subheader("Evidence Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Detected Skills", total_detected)

with col2:
    st.metric("Listed Skills", listed_count)

with col3:
    st.metric("Demonstrated Skills", demonstrated_count)


# =====================================================
# 5. EVIDENCE DISTRIBUTION
# =====================================================

st.divider()

st.subheader("Evidence Distribution")

type_counts = {
    "Listed": 0,
    "Demonstrated": 0,
    "Professional Experience": 0,
    "Other Context": 0
}

type_colors = {
    "Listed": "#3B82F6",
    "Demonstrated": "#22C55E",
    "Professional Experience": "#A78BFA",
    "Other Context": "#64748B"
}

for item in evidence_items:
    for evidence in item.get("evidence", []):

        evidence_type = evidence.get("evidence_type", "")

        if evidence_type == "listed":
            type_counts["Listed"] += 1

        elif evidence_type == "demonstrated":
            type_counts["Demonstrated"] += 1

        elif evidence_type == "professional_experience":
            type_counts["Professional Experience"] += 1

        else:
            type_counts["Other Context"] += 1


chart_col, explanation_col = st.columns([1.2, 1])

with chart_col:

    if sum(type_counts.values()) > 0:

        evidence_chart = go.Figure(
            data=[
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.68,
                    sort=False,
                    marker=dict(
                        colors=list(type_colors.values()),
                        line=dict(color="#1E293B", width=3)
                    ),
                    textinfo="percent",
                    textfont=dict(
                        family="Manrope",
                        color="#F8FAFC",
                        size=12
                    ),
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Evidence records: %{value}<br>"
                        "Share: %{percent}"
                        "<extra></extra>"
                    )
                )
            ]
        )

        evidence_chart.update_layout(
            template="plotly_dark",
            height=290,
            autosize=True,
            margin=dict(t=10, b=45, l=10, r=10),
            paper_bgcolor="#1E293B",
            plot_bgcolor="#1E293B",
            font=dict(family="Manrope", color="#CBD5E1"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            annotations=[
                dict(
                    text=f"<b>{sum(type_counts.values())}</b><br>"
                         "<span style='font-size:11px'>Records</span>",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        family="Manrope",
                        size=20,
                        color="#F8FAFC"
                    )
                )
            ]
        )

        st.plotly_chart(
            evidence_chart,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "responsive": True
            }
        )

    else:
        st.info("No evidence records are available for visualisation.")


with explanation_col:

    st.markdown("**Classification Summary**")

    for label, count in type_counts.items():

        st.markdown(
            f"""
            <div class="evidence-type-row">
                <span class="evidence-type-dot"
                      style="background:{type_colors[label]}"></span>
                <span class="evidence-type-name">{label}</span>
                <strong>{count}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.caption(
        "These figures count individual evidence records. "
        "A single skill can have more than one record."
    )


# =====================================================
# 6. SEARCH AND FILTER
# =====================================================

st.divider()

st.subheader("Detected Technical Skills")

st.caption(
    "Select a skill to inspect the resume text that supports its detection."
)

search_col, filter_col = st.columns([1.5, 1])

with search_col:
    search_query = st.text_input(
        "Search skills",
        placeholder="Search Python, Java, SQL...",
        key="evidence_search"
    )

with filter_col:
    category_options = ["All Categories"] + sorted({
        item.get("category", "Uncategorised")
        for item in evidence_items
    })

    selected_category = st.selectbox(
        "Filter by category",
        category_options,
        key="evidence_category_filter"
    )


# =====================================================
# 7. FILTER SKILLS
# =====================================================

filtered_items = []

for item in evidence_items:

    skill = item.get("skill", "Unknown Skill")
    category = item.get("category", "Uncategorised")

    matches_search = search_query.lower() in skill.lower()

    matches_category = (
        selected_category == "All Categories"
        or category == selected_category
    )

    if matches_search and matches_category:
        filtered_items.append(item)


st.markdown(
    f'<div class="evidence-results-count">'
    f'Showing <strong>{len(filtered_items)}</strong> of '
    f'<strong>{total_detected}</strong> detected skills'
    f'</div>',
    unsafe_allow_html=True
)


# =====================================================
# 8. SKILL EVIDENCE DETAILS
# =====================================================

if filtered_items:

    for item in filtered_items:

        skill = item.get("skill", "Unknown Skill")
        category = item.get("category", "Uncategorised")
        evidence_list = item.get("evidence", [])

        listed = any(
            evidence.get("evidence_type") == "listed"
            for evidence in evidence_list
        )

        demonstrated = any(
            evidence.get("evidence_type") == "demonstrated"
            for evidence in evidence_list
        )

        with st.expander(
            f"{skill}  ·  {category}  ·  {len(evidence_list)} evidence record(s)",
            expanded=False
        ):

            if listed:
                st.markdown(
                    '<span class="evidence-pill listed">Listed</span>',
                    unsafe_allow_html=True
                )

            if demonstrated:
                st.markdown(
                    '<span class="evidence-pill demonstrated">Demonstrated</span>',
                    unsafe_allow_html=True
                )

            if not listed and not demonstrated:
                st.markdown(
                    '<span class="evidence-pill other">Other Context</span>',
                    unsafe_allow_html=True
                )

            st.markdown("")

            if evidence_list:

                for index, evidence in enumerate(evidence_list):

                    section = html.escape(str(
                        evidence.get("section", "Unknown Section")
                    ))

                    evidence_type = html.escape(str(
                        evidence.get(
                            "evidence_type",
                            "context not classified"
                        )
                    ).replace("_", " ").title())

                    supporting_text = html.escape(str(
                        evidence.get("text", "No supporting text available.")
                    ))

                    st.markdown(
                        f"""
                        <div class="evidence-record">
                            <div class="evidence-record-header">
                                <span class="evidence-record-number">
                                    RECORD {index + 1}
                                </span>
                                <span class="evidence-record-type">
                                    {evidence_type}
                                </span>
                            </div>
                            <div class="evidence-record-section">
                                <span>RESUME SECTION</span>
                                <strong>{section}</strong>
                            </div>
                            <div class="evidence-record-text">
                                {supporting_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:
                st.info(
                    "No supporting text was extracted for this skill."
                )

elif evidence_items:
    st.info("No skills match your search or selected category.")

else:
    st.info(
        "No technical skill evidence was detected in this resume."
    )


# =====================================================
# 9. EXPLANATION AND LIMITATIONS
# =====================================================

st.divider()

st.subheader("Understanding the Classification")

explanation_col1, explanation_col2 = st.columns(2)

with explanation_col1:

    st.markdown(
        """
        **Listed**

        The skill was found under a recognised skills-related heading.

        **Demonstrated**

        The skill was found under a recognised projects section.
        """
    )

with explanation_col2:

    st.markdown(
        """
        **Professional Experience**

        The skill was found under a recognised work experience or internship section.

        **Other Context**

        The skill was detected, but its surrounding section could not be classified.
        """
    )

st.warning(
    "Evidence classification is based on resume headings and extracted text. "
    "It does not independently verify the candidate's actual skill proficiency."
)
