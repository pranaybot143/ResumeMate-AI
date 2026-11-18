from skill_extractor import extract_skill_evidence

sample_resume = """
TECHNICAL SKILLS
Python, Java, SQL, React

PROJECTS
Developed a student management system using Java.
Created a data analysis project using Python.

WORK EXPERIENCE
Used SQL to retrieve and manage database records.
Developed internal tools using Python.

EDUCATION
Bachelor of Engineering in Information Technology.
"""

results = extract_skill_evidence(sample_resume)

for item in results:
    print(f"\nSkill: {item['skill']}")

    for evidence in item["evidence"]:
        print(f"  Section: {evidence['section']}")
        print(f"  Type: {evidence['evidence_type']}")
        print(f"  Evidence: {evidence['text']}")