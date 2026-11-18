import re


TECHNICAL_SKILLS = {
    "Programming Languages": {
        "Python": ["python", "py"],
        "Java": ["java"],
        "JavaScript": ["javascript", "js"],
        "C++": ["c++"],
        "C": ["c language"],
        "PHP": ["php"],
    },
    "Frontend Development": {
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "React": ["react", "reactjs"],
        "Angular": ["angular", "angularjs"],
        "Vue.js": ["vue", "vuejs"],
        "Bootstrap": ["bootstrap"],
    },
    "Backend Development": {
        "Node.js": ["node.js", "nodejs", "node"],
        "Express.js": ["express.js", "expressjs", "express"],
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "REST API": ["rest api", "restful api", "rest apis"],
    },
    "Databases": {
        "SQL": ["sql"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "PostgreSQL": ["postgresql", "postgres"],
        "SQLite": ["sqlite"],
        "Oracle": ["oracle database"],
    },
    "Developer Tools": {
        "Git": ["git"],
        "GitHub": ["github"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes"],
        "Postman": ["postman"],
        "VS Code": ["vs code", "visual studio code"],
    },
    "Core Concepts": {
        "Data Structures": ["data structures", "dsa"],
        "Algorithms": ["algorithms"],
        "Object-Oriented Programming": [
            "object oriented programming",
            "oop",
        ],
        "Machine Learning": ["machine learning", "ml"],
        "Artificial Intelligence": ["artificial intelligence", "ai"],
        "Data Analysis": ["data analysis"],
    },
}


# Common resume headings and their evidence classifications.
SECTION_RULES = {
    "Skills": {
        "type": "listed",
        "patterns": [
            r"\btechnical skills\b",
            r"\bskills\b",
            r"\btechnical proficiencies\b",
            r"\btechnologies\b",
            r"\btools and technologies\b",
        ],
    },
    "Projects": {
        "type": "demonstrated",
        "patterns": [
            r"\bprojects\b",
            r"\bacademic projects\b",
            r"\bpersonal projects\b",
            r"\bproject experience\b",
        ],
    },
    "Professional Experience": {
        "type": "professional experience",
        "patterns": [
            r"\bwork experience\b",
            r"\bprofessional experience\b",
            r"\bemployment history\b",
            r"\bwork history\b",
            r"\binternship experience\b",
            r"\binternships\b",
            r"\bexperience\b",
        ],
    },
}


def _build_skill_pattern(alias):
    """Match a complete alias rather than a partial word."""
    return re.compile(
        r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
        flags=re.IGNORECASE,
    )


def _normalise_heading(line):
    """Prepare a line for resume-heading comparison."""
    line = re.sub(r"^[\s•*\-–—]+", "", line)
    line = re.sub(r"[\s:|]+$", "", line)
    return line.strip().lower()


def _detect_section(line, current_section):
    """
    Detect whether a line is a known resume heading.
    Return the section name and evidence type.
    """
    heading = _normalise_heading(line)

    for section_name, rule in SECTION_RULES.items():
        for pattern in rule["patterns"]:
            if re.fullmatch(pattern, heading, flags=re.IGNORECASE):
                return section_name, rule["type"]

    return current_section


def _split_resume_into_units(text):
    """
    Split text into lines/sentences while carrying the current section
    heading forward to the following content.
    """
    units = []
    current_section = "Other"
    current_type = "context not classified"

    lines = text.replace("\r", "\n").split("\n")

    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()

        if not line:
            continue

        detected = _detect_section(line, current_section)

        if isinstance(detected, tuple):
            current_section, current_type = detected
            continue

        # Split multiple sentences on the same line, keeping the section.
        sentences = re.split(r"(?<=[.!?])\s+", line)

        for sentence in sentences:
            sentence = sentence.strip(" \t•*-–—")

            if sentence:
                units.append({
                    "text": sentence,
                    "section": current_section,
                    "evidence_type": current_type,
                })

    return units


def extract_skill_evidence(text):
    """
    Extract recognised skills with their resume section and evidence type.

    Evidence types:
    - listed: skill found under a skills-related heading
    - demonstrated: skill found under a projects-related heading
    - professional experience: skill found under an employment-related heading
    - context not classified: skill found outside a recognised heading

    This classifies where a skill is mentioned; it does not prove proficiency.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    units = _split_resume_into_units(text)
    results = []

    for category, skills in TECHNICAL_SKILLS.items():
        for standard_name, aliases in skills.items():
            patterns = [
                _build_skill_pattern(alias)
                for alias in aliases
            ]

            evidence = []

            for unit in units:
                if any(pattern.search(unit["text"]) for pattern in patterns):
                    evidence.append({
                        "section": unit["section"],
                        "evidence_type": unit["evidence_type"],
                        "text": unit["text"],
                    })

            if evidence:
                # Remove duplicate evidence entries but preserve order.
                seen = set()
                unique_evidence = []

                for item in evidence:
                    identity = (
                        item["section"],
                        item["evidence_type"],
                        item["text"].casefold(),
                    )

                    if identity not in seen:
                        seen.add(identity)
                        unique_evidence.append(item)

                results.append({
                    "skill": standard_name,
                    "category": category,
                    "evidence": unique_evidence[:10],
                })

    return results


def extract_skills(text):
    """
    Backward-compatible function: returns only a list of skill names.
    Existing app.py can continue using this function unchanged.
    """
    return [
        item["skill"]
        for item in extract_skill_evidence(text)
    ]
