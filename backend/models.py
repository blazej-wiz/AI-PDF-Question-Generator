from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    cards: Mapped[list["Card"]] = relationship("Card", back_populates="document", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), index=True, nullable=False)

    type: Mapped[str] = mapped_column(String(10), nullable=False)  # "mcq" | "saq"
    question: Mapped[str] = mapped_column(Text, nullable=False)

    # Stored as JSON string for MCQ; null for SAQ
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # For MCQ: "A"/"B"/"C"/"D"; null for SAQ
    correct_answer: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # For SAQ: answer text; null for MCQ
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # For future "no overlap" + dedupe
    fingerprint: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="cards")
    progress: Mapped["Progress | None"] = relationship("Progress", back_populates="card", uselist=False, cascade="all, delete-orphan")


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("cards.id"), unique=True, index=True, nullable=False)

    times_seen: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    card: Mapped["Card"] = relationship("Card", back_populates="progress")
