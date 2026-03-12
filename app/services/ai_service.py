import json
import logging
from typing import List, Dict, Optional
from groq import Groq
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.allocation import Allocation
from app.models.enums import AllocationStatus

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_client() -> Optional[Groq]:
    """Get a Groq client. Returns None if API key is not configured."""
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
        return None
    return Groq(api_key=settings.GROQ_API_KEY)


def _call_groq(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Make a Groq API call. Returns the response text or None on failure."""
    client = _get_client()
    if not client:
        logger.warning("Groq API key not configured. AI features disabled.")
        return None

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        return None


# --- Company Profile ---
COMPANY_PROFILE = """
Company: Smart-Alloc Solutions
Industry: Technology & Software Development
Team Size: Variable (check current employee count)
Capabilities:
- Web Development (Frontend & Backend)
- Mobile App Development
- Data Science & Machine Learning
- Cloud Infrastructure & DevOps
- UI/UX Design
- Project Management
- Quality Assurance & Testing
- Database Design & Administration
- API Development & Integration
- Cybersecurity
Current Capacity: Based on employee workload data provided
"""


def evaluate_project(
    project_title: str,
    project_description: str,
    project_deadline: str,
    project_budget: Optional[float],
    required_skills: List[str],
    employee_count: int,
    available_skills: List[str],
    active_project_count: int,
) -> Dict:
    """AI-powered project viability assessment.
    Returns dict with decision, confidence, reasoning, risk_factors."""

    system_prompt = """You are a project viability analyst for a technology company.
Given the company's capabilities and current workload, evaluate whether this project should be accepted or rejected.

You MUST return valid JSON with exactly these fields:
{
    "decision": "accept" or "reject" or "needs_review",
    "confidence": 0.0 to 1.0,
    "reasoning": "string explaining the decision",
    "risk_factors": ["list", "of", "risk", "factors"],
    "suggestions": "any suggestions for the company"
}"""

    user_prompt = f"""
{COMPANY_PROFILE}

Current Status:
- Total Employees: {employee_count}
- Active Projects: {active_project_count}
- Available Skills in Company: {', '.join(available_skills) if available_skills else 'N/A'}

Project to Evaluate:
- Title: {project_title}
- Description: {project_description}
- Deadline: {project_deadline or 'Not specified'}
- Budget: ${project_budget:,.2f} if {project_budget} else 'Not specified'
- Required Skills: {', '.join(required_skills) if required_skills else 'Not specified'}

Evaluate this project considering:
1. Does the company have the required skills?
2. Is the deadline realistic given current workload?
3. Are there enough available employees?
4. Are there any significant risk factors?

Return your analysis as JSON."""

    response = _call_groq(system_prompt, user_prompt)

    if not response:
        return {
            "decision": "needs_review",
            "confidence": 0.0,
            "reasoning": "AI service unavailable. Manual review required.",
            "risk_factors": ["AI evaluation could not be completed"],
            "suggestions": "Please review manually.",
        }

    try:
        result = json.loads(response)
        # Validate required fields
        required_fields = {"decision", "confidence", "reasoning", "risk_factors"}
        if not all(f in result for f in required_fields):
            raise ValueError("Missing required fields in AI response")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI response: {e}")
        return {
            "decision": "needs_review",
            "confidence": 0.0,
            "reasoning": f"AI response could not be parsed. Raw: {response[:200]}",
            "risk_factors": ["AI response parsing failed"],
            "suggestions": "Please review manually.",
        }


def suggest_employees(
    db: Session,
    project_id: int,
    project_title: str,
    project_description: str,
    required_skills: List[str],
    candidates: List[Dict],
) -> List[Dict]:
    """AI-powered employee matching.
    candidates: list of dicts {id, name, skills: [{name, proficiency}], workload_percent}
    Returns list of {employee_id, match_score, reasoning}."""

    if not candidates:
        return []

    system_prompt = """You are an HR allocation assistant for a technology company.
Given a project's requirements and a list of candidate employees with their skills and current workload,
rank the best matches for this project.

You MUST return valid JSON with exactly this structure:
{
    "suggestions": [
        {
            "employee_id": 123,
            "match_score": 0.0 to 1.0,
            "reasoning": "why this employee is a good match"
        }
    ]
}

Rank employees by:
1. Skill match (most important)
2. Proficiency level in required skills
3. Current workload (prefer less busy employees)
Only include employees with match_score >= 0.3.
Return at most 10 suggestions, sorted by match_score descending."""

    # Build candidate list (use IDs only, no PII)
    candidate_descriptions = []
    for c in candidates:
        skills_str = ", ".join(
            f"{s['name']} (level {s['proficiency']})" for s in c.get("skills", [])
        )
        candidate_descriptions.append(
            f"- Employee #{c['id']}: Skills: [{skills_str}], Current Workload: {c['workload_percent']}%"
        )

    user_prompt = f"""
Project: {project_title}
Description: {project_description}
Required Skills: {', '.join(required_skills)}

Candidate Employees:
{chr(10).join(candidate_descriptions)}

Rank these employees for the project. Return JSON with your suggestions."""

    response = _call_groq(system_prompt, user_prompt)

    if not response:
        # Fallback: simple skill-matching without AI
        return _simple_skill_match(candidates, required_skills)

    try:
        result = json.loads(response)
        suggestions = result.get("suggestions", [])

        # Validate employee IDs exist in candidates
        valid_ids = {c["id"] for c in candidates}
        validated = []
        for s in suggestions:
            if s.get("employee_id") in valid_ids:
                validated.append({
                    "employee_id": s["employee_id"],
                    "match_score": min(1.0, max(0.0, float(s.get("match_score", 0.5)))),
                    "reasoning": s.get("reasoning", ""),
                })

        # Save as AI suggestions in DB
        from app.services.allocation_service import remove_ai_suggestions_for_project
        remove_ai_suggestions_for_project(db, project_id)

        for s in validated:
            allocation = Allocation(
                project_id=project_id,
                employee_id=s["employee_id"],
                status=AllocationStatus.SUGGESTED_BY_AI,
                ai_match_score=s["match_score"],
            )
            db.add(allocation)
        db.commit()

        return validated

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI employee suggestions: {e}")
        return _simple_skill_match(candidates, required_skills)


def _simple_skill_match(candidates: List[Dict], required_skills: List[str]) -> List[Dict]:
    """Fallback: simple skill matching without AI."""
    required_lower = {s.lower() for s in required_skills}
    results = []

    for c in candidates:
        employee_skills = {s["name"].lower(): s["proficiency"] for s in c.get("skills", [])}
        matching = required_lower & set(employee_skills.keys())

        if matching:
            score = len(matching) / max(len(required_lower), 1)
            # Adjust by proficiency
            avg_proficiency = sum(employee_skills[s] for s in matching) / len(matching) / 5.0
            score = (score * 0.7) + (avg_proficiency * 0.3)
            # Penalize high workload
            workload_penalty = c.get("workload_percent", 0) / 200.0
            score = max(0.0, score - workload_penalty)

            results.append({
                "employee_id": c["id"],
                "match_score": round(score, 2),
                "reasoning": f"Matches {len(matching)}/{len(required_lower)} required skills (fallback matching)",
            })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:10]
