from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.controller.deps import get_db
router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    # Just ensures the dependency resolves and session opens
    return {"status": "ok", "db": "session_created"}