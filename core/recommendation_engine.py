import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load API key from the root .env file.
load_dotenv()

# Keep the existing dictionary as a fallback if Gemini is unavailable.
SKILL_RECOMMENDATIONS = {
    "Python": "Practise Python fundamentals, OOP and problem-solving.",
    "Java": "Strengthen Java programming, OOP and data structures.",
    "JavaScript": "Practise modern JavaScript, ES6+ and asynchronous programming.",
    "React": "Learn React components, hooks, props and state management.",
    "Node.js": "Practise server-side development using Node.js.",
    "Express.js": "Build REST APIs and middleware using Express.js.",
    "SQL": "Practise SQL queries, joins, grouping and subqueries.",
    "MySQL": "Learn database design, joins, indexing and MySQL queries.",
    "MongoDB": "Practise document-based database design and CRUD operations.",
    "PostgreSQL": "Learn relational database design and advanced SQL queries.",
    "Django": "Learn Django fundamentals and build a CRUD web application.",
    "Flask": "Build lightweight Python web applications using Flask.",
    "FastAPI": "Practise creating REST APIs using FastAPI.",
    "REST API": "Learn HTTP methods, status codes and REST API design.",
    "Git": "Practise version control, branching and merging.",
    "GitHub": "Learn repository management, pull requests and collaboration.",
    "Docker": "Learn containerisation and practise creating Docker images.",
    "Machine Learning": (
        "Study supervised learning, model evaluation and data preprocessing."
    )
}


def _fallback_result(missing_skills, warning):
    """Return useful basic recommendations when Gemini cannot be reached."""

    recommendations = []

    for skill in missing_skills:
        recommendation = SKILL_RECOMMENDATIONS.get(
            skill,
            f"Explore {skill} and practise it through a small project."
        )

        recommendations.append({
            "skill": skill,
            "recommendation": recommendation
        })

    return {
        "source": "fallback",
        "warning": warning,
        "recommendations": recommendations,
        "ai_feedback": {
            "overall_feedback": (
                "Personalised AI feedback could not be generated at this time. "
                "Basic skill recommendations are provided instead."
            ),
            "strengths": [],
            "improvement_areas": [],
            "learning_roadmap": [],
            "project_suggestions": [],
            "resume_tips": []
        }
    }


def generate_recommendations(
    resume_text,
    job_description,
    matching_skills,
    missing_skills,
    resume_skill_evidence=None
):
    """
    Generate contextual resume feedback and skill recommendations with Gemini.

    The return structure is stable so the Streamlit dashboard can display
    Gemini output or fallback recommendations in the same way.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return _fallback_result(
            missing_skills,
            "GEMINI_API_KEY was not found. Check your root .env file."
        )

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30000,
                retry_options=types.HttpRetryOptions(attempts=1)
            )
        )

        # Limit input size to keep requests manageable.
        resume_excerpt = resume_text[:12000]
        job_excerpt = job_description[:8000]
        evidence_data = resume_skill_evidence or []

        prompt = f"""
You are ResumeMate AI, a practical career and resume advisor.

Analyse the candidate's resume against the target job description.
Use only evidence supported by the supplied text. Do not invent experience,
qualifications, projects, achievements, or skills.

Candidate resume text:
{resume_excerpt}

Target job description:
{job_excerpt}

Skills found in both resume and job description:
{json.dumps(matching_skills)}

Skills required by the job description but not found in the resume:
{json.dumps(missing_skills)}

Extracted skill evidence from the resume (section, evidence type, and text):
{json.dumps(evidence_data, ensure_ascii=False)}

Return ONLY a valid JSON object with exactly these keys:
{{
  "overall_feedback": "A concise, balanced assessment of the candidate's alignment.",
  "strengths": ["Evidence-based strength 1", "Evidence-based strength 2"],
  "improvement_areas": ["Specific improvement 1", "Specific improvement 2"],
  "learning_roadmap": ["Prioritised learning step 1", "Prioritised learning step 2"],
  "project_suggestions": ["Relevant practical project idea 1", "Project idea 2"],
  "resume_tips": ["Specific resume improvement 1", "Specific resume improvement 2"],
  "recommendations": [
    {{
      "skill": "Exact missing skill name",
      "recommendation": "Contextual explanation and a practical next step."
    }}
  ]
}}

Rules:
- Keep feedback constructive, realistic and specific to this candidate.
- Use the supplied skill evidence to distinguish listed skills from skills mentioned in projects or professional experience.
- Do not treat a listed skill as proof of practical experience.
- Refer to the section and evidence text when discussing demonstrated skills.
- If evidence is classified as context not classified, do not guess its resume section.
- Do not claim that the candidate is qualified or unqualified for the job.
- Prioritise the missing skills according to the job description.
- If a missing skill exists, include one recommendation for each missing skill.
- Do not recommend a missing skill as something the candidate already knows.
- If a section has no useful items, return an empty array.
- Do not include Markdown fences or text outside the JSON object.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        result = json.loads(response.text)

        # Validate and normalise all expected fields.
        ai_feedback = {
            "overall_feedback": str(result.get("overall_feedback", "")),
            "strengths": _string_list(result.get("strengths")),
            "improvement_areas": _string_list(
                result.get("improvement_areas")
            ),
            "learning_roadmap": _string_list(
                result.get("learning_roadmap")
            ),
            "project_suggestions": _string_list(
                result.get("project_suggestions")
            ),
            "resume_tips": _string_list(result.get("resume_tips"))
        }

        recommendations = []
        returned_recommendations = result.get("recommendations", [])

        if isinstance(returned_recommendations, list):
            for item in returned_recommendations:
                if not isinstance(item, dict):
                    continue

                skill = str(item.get("skill", "")).strip()
                recommendation = str(
                    item.get("recommendation", "")
                ).strip()

                if skill and recommendation:
                    recommendations.append({
                        "skill": skill,
                        "recommendation": recommendation
                    })

        # Ensure every missing skill has a recommendation even if Gemini
        # omits one from its response.
        existing_skills = {
            item["skill"].casefold() for item in recommendations
        }

        for skill in missing_skills:
            if skill.casefold() not in existing_skills:
                recommendations.append({
                    "skill": skill,
                    "recommendation": SKILL_RECOMMENDATIONS.get(
                        skill,
                        f"Explore {skill} and practise it through a small project."
                    )
                })

        return {
            "source": "gemini",
            "warning": "",
            "recommendations": recommendations,
            "ai_feedback": ai_feedback
        }

    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as error:
        return _fallback_result(
            missing_skills,
            f"Gemini returned an unexpected response. Basic recommendations "
            f"are shown instead. Details: {error}"
        )

    except Exception as error:
        return _fallback_result(
            missing_skills,
            "Gemini could not be reached. Basic recommendations are shown "
            f"instead. Details: {error}"
        )


def _string_list(value):
    """Keep only non-empty strings from a JSON array."""

    if not isinstance(value, list):
        return []

    return [
        item.strip()
        for item in value
        if isinstance(item, str) and item.strip()
    ]
