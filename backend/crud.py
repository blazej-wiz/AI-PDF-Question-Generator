import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.models import Document, Card, Progress


def _fingerprint_question(question: str) -> str:
    normalized = " ".join((question or "").strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ---- Documents ----
def create_document(db: Session, title: str) -> Document:
    doc = Document(title=title.strip())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def list_documents(db: Session) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.created_at.desc())))


def get_document(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


# ---- Cards ----
def add_cards_to_document(db: Session, document_id: int, cards: list[dict]) -> list[Card]:
    created: list[Card] = []

    for c in cards:
        q_type = (c.get("type") or "").strip().lower()
        question = (c.get("question") or "").strip()

        if not question or q_type not in ("mcq", "saq"):
            continue

        options = c.get("options")
        options_json = json.dumps(options) if isinstance(options, list) else None

        card = Card(
            document_id=document_id,
            type=q_type,
            question=question,
            options_json=options_json,
            correct_answer=(c.get("correct_answer") or None),
            answer=(c.get("answer") or None),
            explanation=(c.get("explanation") or None),
            fingerprint=_fingerprint_question(question),
        )
        db.add(card)
        created.append(card)

    db.commit()
    for card in created:
        db.refresh(card)
    return created


def get_cards_for_document(db: Session, document_id: int) -> list[Card]:
    stmt = select(Card).where(Card.document_id == document_id).order_by(Card.created_at.asc())
    return list(db.scalars(stmt))


# ---- Progress ----
def record_progress(db: Session, card_id: int, correct: bool) -> Progress:
    prog = db.scalar(select(Progress).where(Progress.card_id == card_id))
    if prog is None:
        prog = Progress(card_id=card_id, times_seen=0, times_correct=0)
        db.add(prog)

    prog.times_seen += 1
    if correct:
        prog.times_correct += 1
    prog.last_seen_at = datetime.utcnow()

    db.commit()
    db.refresh(prog)
    return prog
