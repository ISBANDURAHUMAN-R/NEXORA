from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.demo_seed import reset_demo_data

router = APIRouter(prefix="/api/demo", tags=["Demo"])

@router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    reset_demo_data(db)
    return {"message": "Demo data reset successfully to default AI & Full-Stack Engineer tree."}
