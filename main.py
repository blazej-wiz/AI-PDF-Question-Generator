# Root entrypoint (keeps: uvicorn main:app --reload)
from backend.main import app  # noqa: F401
