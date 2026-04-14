from langchain_core.prompts import ChatPromptTemplate

extraction_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """Extract professional details from the resume and return only facts explicitly present.

Output in this exact markdown structure:
## Candidate Snapshot
- Name:
- Current Role:
- Total Experience (if explicitly stated):

## Skills
- Technical Skills:
- Tools/Platforms:
- Domains:

## Education & Certifications
- Education:
- Certifications:

## Key Evidence
- Quote 3 to 5 short evidence lines copied/paraphrased from resume text.

Rules:
- Do NOT infer missing details.
- If a field is unavailable, write "Not mentioned".
""",
    ),
    ("human", "Resume Content: {resume_text}")
])

jd_extraction_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """Extract and organize critical hiring requirements from a Job Description.

Return output in this exact markdown structure:
## Role Overview
- Job Title:
- Seniority:
- Experience Required:

## Core Requirements
- Must-Have Skills:
- Nice-to-Have Skills:
- Tools/Platforms:

## Responsibilities
- 4 to 8 concise bullets

## Evaluation Priorities
- Mention the top 5 signals a recruiter should verify in screening.

Rules:
- Use only information present in the JD.
- If a detail is not available, write "Not mentioned".
""",
    ),
    ("human", "Job Description Content: {job_description}")
])

screening_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert technical recruiter. Compare extracted candidate profile with the Job Description.

Scoring framework:
- Skill Match: 40%
- Experience Relevance: 40%
- Tool/Platform Alignment: 20%

Return response in this exact markdown layout:
## Decision Summary
- Recommendation: Strong Fit | Moderate Fit | Low Fit
- Fit Score: <0-100>/100

## Score Breakdown
- Skill Match (0-40):
- Experience Relevance (0-40):
- Tool/Platform Alignment (0-20):

## Matched Strengths
- 4 to 6 bullet points

## Missing or Weak Areas
- 3 to 6 bullet points

## Interview Focus Areas
- 3 to 5 targeted interview questions based on gaps.

Rules:
- Be strict and evidence-based.
- Do NOT fabricate candidate experience.
- Keep language concise and recruiter-professional.
""",
    ),
    ("human", "Extracted Skills: {extracted_data}\n\nJob Description: {job_description}")
])