import json
import os
import random
import re
import string
from openai import OpenAI


# ---- OpenAI client ----
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---- Quality / cleanup helpers ----
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
        key = " ".join(text.split())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(q)
    return out


def strip_option_label(s: str) -> str:
    """
    Removes leading labels like 'A. ', 'B) ', 'C - ', 'D:' from an option string.
    """
    if not isinstance(s, str):
        return s
    return re.sub(r"^\s*[A-D]\s*[\)\.\:\-]\s*", "", s.strip(), flags=re.IGNORECASE)


def normalize_mcq(question: dict) -> dict:
    if not isinstance(question, dict):
        return question

    # ✅ Ensure type is always present
    if not question.get("type"):
        question["type"] = "mcq"

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

    # Strip any "A. " prefixes the model may include inside options
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

    if not question.get("type"):
        question["type"] = "saq"

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


# ---- Prompt + generation ----
def build_chunk_prompt(*, question_type: str, per_chunk: int, chunk: str, chunk_index: int, chunk_total: int) -> str:
    return f"""
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
- Include the key "type" with value "mcq"

SAQ RULES (if SAQ)
- Provide a question and a concise model answer (2–4 sentences).
- Use the key "answer" exactly (do not use other keys).
- Include the key "type" with value "saq"

OUTPUT FORMAT (STRICT)
- Return ONLY valid JSON.
- Output must be a JSON array of objects.
- No markdown, no commentary, no extra text.

CHUNK {chunk_index}/{chunk_total}:
{chunk}
""".strip()


def generate_questions_from_chunks(*, question_type: str, count: int, chunks: list[str]) -> list[dict]:
    if not chunks:
        return []

    per_chunk = max(1, (count + len(chunks) - 1) // len(chunks))
    all_questions: list[dict] = []

    for i, chunk in enumerate(chunks, start=1):
        prompt = build_chunk_prompt(
            question_type=question_type,
            per_chunk=per_chunk,
            chunk=chunk,
            chunk_index=i,
            chunk_total=len(chunks),
        )

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

    # Filter + dedupe
    all_questions = [q for q in all_questions if not is_meta_question(q.get("question", ""))]
    all_questions = dedupe_questions(all_questions)

    # Trim
    all_questions = all_questions[:count]

    # Normalize
    if question_type == "mcq":
        all_questions = [normalize_mcq(q) for q in all_questions]
    else:
        all_questions = [normalize_saq(q) for q in all_questions]

    return all_questions


def explain_answer(*, question: str, correct_answer: str) -> str:
    prompt = f"""
You are an educational tutor.

Explain why the following answer is correct.
Keep the explanation clear, concise, and beginner-friendly.

Question:
{question}

Correct Answer:
{correct_answer}
""".strip()

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )
    return response.output_text
