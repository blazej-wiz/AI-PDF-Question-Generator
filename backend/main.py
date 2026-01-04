from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import GenerateQuestionsResponse, ExplainRequest
from backend.services.pdf import extract_pdf_text, chunk_text, pick_spread_chunks
from backend.services.generation import generate_questions_from_chunks, explain_answer
from backend.db import engine
from backend.models import Base
from backend.routes.documents import router as documents_router
from backend.routes.progress import router as progress_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(documents_router)
app.include_router(progress_router)


@app.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(
    file: UploadFile = File(...),
    question_type: str = Form(...),
    count: int = Form(5),
):
    if question_type not in ["mcq", "saq"]:
        return {"error": "question_type must be 'mcq' or 'saq'"}

    if count not in [5, 10, 15, 20]:
        return {"error": "count must be one of: 5, 10, 15, 20"}

    text = extract_pdf_text(file.file)
    if not text.strip():
        return {"error": "No extractable text found in the PDF"}

    chunks = chunk_text(text, max_chars=1800)
    selected_chunks = pick_spread_chunks(chunks, max_chunks=4)

    if not selected_chunks:
        return {"error": "No extractable text found in the PDF"}

    questions = generate_questions_from_chunks(
        question_type=question_type,
        count=count,
        chunks=selected_chunks,
    )

    if not questions:
        return {
            "error": "No valid questions could be generated from the PDF text",
            "raw_output": "All chunk generations failed or returned empty.",
        }

    return {
        "question_type": question_type,
        "count": len(questions),
        "questions": questions,
    }


@app.post("/explain-question")
async def explain_question(data: ExplainRequest):
    explanation = explain_answer(
        question=data.question,
        correct_answer=data.correct_answer,
    )
    return {"explanation": explanation}
