import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import crud
from backend.schemas import DocumentCreate, DocumentOut, CardsBulkIn, CardOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    doc = crud.create_document(db, payload.title)
    return {
        "id": doc.id,
        "title": doc.title,
        "created_at": doc.created_at.isoformat(),
    }


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    docs = crud.list_documents(db)
    return [
        {"id": d.id, "title": d.title, "created_at": d.created_at.isoformat()}
        for d in docs
    ]


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "title": doc.title, "created_at": doc.created_at.isoformat()}


@router.post("/{document_id}/cards", response_model=list[CardOut])
def add_cards(document_id: int, payload: CardsBulkIn, db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    created = crud.add_cards_to_document(db, document_id, payload.cards)

    out: list[dict] = []
    for c in created:
        options = None
        if c.options_json:
            try:
                options = json.loads(c.options_json)
            except Exception:
                options = None

        out.append(
            {
                "id": c.id,
                "document_id": c.document_id,
                "type": c.type,
                "question": c.question,
                "options": options,
                "correct_answer": c.correct_answer,
                "answer": c.answer,
                "explanation": c.explanation,
            }
        )
    return out


@router.get("/{document_id}/cards", response_model=list[CardOut])
def get_cards(document_id: int, db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    cards = crud.get_cards_for_document(db, document_id)

    out: list[dict] = []
    for c in cards:
        options = None
        if c.options_json:
            try:
                options = json.loads(c.options_json)
            except Exception:
                options = None

        out.append(
            {
                "id": c.id,
                "document_id": c.document_id,
                "type": c.type,
                "question": c.question,
                "options": options,
                "correct_answer": c.correct_answer,
                "answer": c.answer,
                "explanation": c.explanation,
            }
        )
    return out
