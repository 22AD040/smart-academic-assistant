from google import genai
from app.config import GEMINI_API_KEY, MODEL_NAME
from app.core.retrieval import retrieve

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_answer(query, role="student"):
    try:
        context_docs = retrieve(query)
    except:
        context_docs = []

    context = "\n".join(context_docs) if context_docs else "No documents available"

    prompt = f"""
You are an advanced academic assistant.

Role: {role}

Context:
{context}

Question:
{query}

Instructions:
- Give detailed, structured ,Longer answers
- Use headings, bullet points
- Be accurate and clear
- Explain concepts step-by-step
- If no context, answer using general knowledge
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text, context_docs