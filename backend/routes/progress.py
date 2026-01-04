from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db import get_db
from backend import crud
from backend.schemas import ProgressIn, ProgressOut

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("", response_model=ProgressOut)
def post_progress(payload: ProgressIn, db: Session = Depends(get_db)):
    prog = crud.record_progress(db, payload.card_id, payload.correct)
    return {
        "card_id": prog.card_id,
        "times_seen": prog.times_seen,
        "times_correct": prog.times_correct,
        "last_seen_at": prog.last_seen_at.isoformat() if prog.last_seen_at else None,
    }
