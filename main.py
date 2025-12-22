from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import os
import json
import random
import string
from openai import OpenAI
from pydantic import BaseModel
from typing import List


# =========================
# Models
# =========================

class MCQ(BaseModel):
    type: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class SAQ(BaseModel):
    type: str
    question: str
    answer: str


class GenerateQuestionsResponse(BaseModel):
    question_type: str
    count: int
    questions: list


class ExplainRequest(BaseModel):
    question: str
    correct_answer: str


# =========================
# App setup
# =========================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Helpers
# =========================

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def normalize_mcq(question: dict) -> dict:
    """
    Normalizes MCQs into a stable schema.

    Handles:
    - options as list: ["A", "B", "C", "D"]
    - options as dict: {"A": "...", "B": "..."}
    - choices / answers aliases
    - reshuffling
    - safe correct_answer recalculation
    """

    raw_options = (
        question.get("options")
        or question.get("choices")
        or question.get("answers")
        or []
    )

    # 🔑 CASE 1: options as dict {"A": "...", "B": "..."}
    if isinstance(raw_options, dict):
        # Preserve order A-D if possible
        ordered = []
        for key in sorted(raw_options.keys()):
            ordered.append(raw_options[key])
        options = ordered

    # 🔑 CASE 2: options already a list
    elif isinstance(raw_options, list):
        options = raw_options

    else:
        question["options"] = []
        return question

    if len(options) < 2:
        question["options"] = []
        return question

    question["options"] = options

    correct_letter = question.get("correct_answer")
    if not isinstance(correct_letter, str) or len(correct_letter) != 1:
        return question

    correct_letter = correct_letter.upper()

    try:
        original_index = string.ascii_uppercase.index(correct_letter)
    except ValueError:
        return question

    if original_index >= len(options):
        return question

    correct_text = options[original_index]

    random.shuffle(options)

    try:
        new_index = options.index(correct_text)
    except ValueError:
        return question

    question["options"] = options
    question["correct_answer"] = string.ascii_uppercase[new_index]

    return question

# =========================
# Routes
# =========================

@app.post(
    "/generate-questions",
    response_model=GenerateQuestionsResponse
)
async def generate_questions(
    file: UploadFile = File(...),
    question_type: str = Form(...)
):
    if question_type not in ["mcq", "saq"]:
        return {
            "error": "question_type must be 'mcq' or 'saq'"
        }

    # 1. Extract text from PDF
    text = extract_pdf_text(file.file)

    if not text.strip():
        return {
            "error": "No extractable text found in the PDF"
        }

    # 2. Build improved prompt
    prompt = f"""
You are an educational assistant.

Based on the text below, generate 5 {question_type.upper()} questions.

Rules:
- If MCQ:
  - Provide exactly 4 options
  - Randomize the order of the options so the correct answer is not always first
  - Set correct_answer to the correct option letter (A, B, C, or D)
  - Include a short explanation
- If SAQ:
  - Provide a question and a concise model answer

Formatting rules:
- Return ONLY valid JSON
- The output must be a JSON array
- No markdown
- No commentary
- No extra text

TEXT:
{text[:3000]}
"""

    # 3. Call OpenAI
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    output_text = response.output_text

    # 4. Parse JSON safely
    try:
        questions = json.loads(output_text)
    except json.JSONDecodeError:
        return {
            "error": "AI returned invalid JSON",
            "raw_output": output_text
        }

    if not isinstance(questions, list):
        return {
            "error": "AI output is not a list of questions",
            "raw_output": questions
        }

    # 5. Normalize MCQs server-side (bulletproof fix)
    if question_type == "mcq":
        questions = [normalize_mcq(q) for q in questions]

    return {
        "question_type": question_type,
        "count": len(questions),
        "questions": questions
    }


@app.post("/explain-question")
async def explain_question(data: ExplainRequest):
    prompt = f"""
You are an educational tutor.

Explain why the following answer is correct.
Keep the explanation clear, concise, and beginner-friendly.

Question:
{data.question}

Correct Answer:
{data.correct_answer}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return {
        "explanation": response.output_text
    }
