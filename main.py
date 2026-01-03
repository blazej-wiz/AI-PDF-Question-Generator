from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import os
import json
import random
import string
from openai import OpenAI
from pydantic import BaseModel
import re


# =========================
# Models
# =========================






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

def is_meta_question(q_text: str) -> bool:
    if not isinstance(q_text, str):
        return True
    t = q_text.strip().lower()
    bad_phrases = [
        "title of the document",
        "title of this document",
        "what is the title",
        "learning objective",
        "learning objectives",
        "what are the objectives",
        "objective of this",
        "what is this document about",
        "main purpose of this document",
        "table of contents",
        "author of",
    ]
    return any(p in t for p in bad_phrases)

def dedupe_questions(questions: list) -> list:
    seen = set()
    out = []
    for q in questions:
        text = (q.get("question") or "").strip().lower()
        key = " ".join(text.split())  # normalize whitespace
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(q)
    return out

def strip_option_label(s: str) -> str:

    if not isinstance(s, str):
        return s
    return re.sub(r"^\s*[A-D]\s*[\)\.\:\-]\s*", "", s.strip(), flags=re.IGNORECASE)

def chunk_text(text: str, max_chars: int = 1800) -> list[str]:

    if not text:
        return []

    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    buf = ""

    for p in paras:

        if len(buf) + len(p) + 1 <= max_chars:
            buf = (buf + "\n" + p).strip() if buf else p
        else:
            if buf:
                chunks.append(buf)
            buf = p

    if buf:
        chunks.append(buf)

    return chunks


def pick_spread_chunks(chunks: list[str], max_chunks: int = 4) -> list[str]:

    if not chunks:
        return []

    if len(chunks) <= max_chunks:
        return chunks


    idxs = [round(i * (len(chunks) - 1) / (max_chunks - 1)) for i in range(max_chunks)]

    idxs = sorted(set(idxs))
    return [chunks[i] for i in idxs]


def normalize_mcq(question: dict) -> dict:


    raw_options = (
        question.get("options")
        or question.get("choices")
        or question.get("answers")
        or []
    )


    if isinstance(raw_options, dict):

        ordered = []
        for key in sorted(raw_options.keys()):
            ordered.append(raw_options[key])
        options = ordered


    elif isinstance(raw_options, list):
        options = raw_options

    else:
        question["options"] = []
        return question

    if len(options) < 2:
        question["options"] = []
        return question

    options = [strip_option_label(opt) for opt in options if isinstance(opt, str)]

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

def normalize_saq(question: dict) -> dict:

    if not isinstance(question, dict):
        return question


    if question.get("type") is None:
        question["type"] = "saq"

    ans = (
        question.get("answer")
        or question.get("model_answer")
        or question.get("correct_answer")
        or question.get("response")
        or question.get("solution")
        or ""
    )


    if not isinstance(ans, str):
        ans = str(ans)

    question["answer"] = ans.strip()
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
    question_type: str = Form(...),
    count: int = Form(5)
):

    if question_type not in ["mcq", "saq"]:
        return {
            "error": "question_type must be 'mcq' or 'saq'"
        }
    if count not in [5, 10, 15, 20]:
        return {"error": "count must be one of: 5, 10, 15, 20"}


    text = extract_pdf_text(file.file)

    chunks = chunk_text(text, max_chars=1800)
    selected_chunks = pick_spread_chunks(chunks, max_chunks=4)

    if not selected_chunks:
        return {"error": "No extractable text found in the PDF"}


    per_chunk = max(1, (count + len(selected_chunks) - 1) // len(selected_chunks))
    all_questions = []

    for i, chunk in enumerate(selected_chunks, start=1):
        prompt = f"""
    You are an educational question-writer.

    TASK
    Generate exactly {per_chunk} {question_type.upper()} questions based ONLY on the text chunk below.
    The questions must test understanding of the subject matter (not the document itself).

    VERY IMPORTANT (avoid low-value questions)
    Do NOT ask questions about:
    - the title of the document / headings / table of contents
    - learning objectives
    - "what is this document about"
    - author/date/formatting/structure

    QUALITY REQUIREMENTS
    - Questions must be specific and content-based.
    - Do not repeat the same question in different wording.
    - Avoid near-duplicates.

    MCQ RULES (if MCQ)
    - Provide exactly 4 options as a list of strings.
    - Set correct_answer to a single letter: A, B, C, or D.
    - Include a short explanation (1–3 sentences).

    SAQ RULES (if SAQ)
- Provide a question and a concise model answer (2–4 sentences).
- Use the key "answer" exactly (do not use other keys).


    OUTPUT FORMAT (STRICT)
    - Return ONLY valid JSON.
    - Output must be a JSON array of objects.
    - No markdown, no commentary, no extra text.

    CHUNK {i}/{len(selected_chunks)}:
    {chunk}
    """

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        output_text = response.output_text

        try:
            part = json.loads(output_text)
            if isinstance(part, list):
                all_questions.extend(part)
        except json.JSONDecodeError:
            continue

    questions = all_questions

    if not questions:
        return {
            "error": "No valid questions could be generated from the PDF text",
            "raw_output": "All chunk generations failed or returned empty."
        }

    if not isinstance(questions, list):
        return {
            "error": "AI output is not a list of questions",
            "raw_output": questions
        }


    questions = [
        q for q in questions
        if not is_meta_question(q.get("question", ""))
    ]


    questions = dedupe_questions(questions)
    questions = questions[:count]

    # 5. Normalize MCQs server-side
    if question_type == "mcq":
        questions = [normalize_mcq(q) for q in questions]
    else:
        questions = [normalize_saq(q) for q in questions]

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
