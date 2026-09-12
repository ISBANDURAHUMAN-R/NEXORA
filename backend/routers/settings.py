from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Settings
from schemas import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return SettingsResponse(
        xp_per_30min=settings.xp_per_30min,
        xp_per_60min=settings.xp_per_60min,
        deep_work_bonus_pct=settings.deep_work_bonus_pct,
        consistency_bonus_pct=settings.consistency_bonus_pct,
        is_demo_mode=settings.is_demo_mode
    )

@router.put("", response_model=SettingsResponse)
def update_settings(update_in: SettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)

    if update_in.xp_per_30min is not None:
        settings.xp_per_30min = update_in.xp_per_30min
    if update_in.xp_per_60min is not None:
        settings.xp_per_60min = update_in.xp_per_60min
    if update_in.deep_work_bonus_pct is not None:
        settings.deep_work_bonus_pct = update_in.deep_work_bonus_pct
    if update_in.consistency_bonus_pct is not None:
        settings.consistency_bonus_pct = update_in.consistency_bonus_pct

    db.commit()
    db.refresh(settings)

    return SettingsResponse(
        xp_per_30min=settings.xp_per_30min,
        xp_per_60min=settings.xp_per_60min,
        deep_work_bonus_pct=settings.deep_work_bonus_pct,
        consistency_bonus_pct=settings.consistency_bonus_pct,
        is_demo_mode=settings.is_demo_mode
    )
