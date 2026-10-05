from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)


def analyze_with_gemini(request_data, policies):

    policy_text = "\n\n".join(policies)

    prompt = f"""
You are the AI Permission Agent for ClassGuard,
an intelligent college classroom access management system.

Analyze the classroom request using ONLY the provided college policies.

CLASSROOM REQUEST:

User ID: {request_data["user_id"]}
Purpose: {request_data["purpose"]}
Date: {request_data["date"]}
Start Time: {request_data["start_time"]}
End Time: {request_data["end_time"]}
Number of Students: {request_data["students"]}
Projector Required: {request_data["projector_required"]}

RELEVANT COLLEGE POLICIES:

{policy_text}

INSTRUCTIONS:

- Consider only the provided policies.
- Do not invent any rules.
- Do not mention rule numbers.
- Explain the relevant rules naturally.
- Give a short and clear reason.
- If additional approval is needed, mention it clearly.

Return exactly:

Decision: APPROVED / REVIEW REQUIRED / REJECTED

Reason:
<short explanation>

The final authorization is handled by the ClassGuard
rule validation system. Your role is to provide an AI
recommendation and explanation.
"""

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    return response.output_text