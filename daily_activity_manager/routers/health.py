"""Health & Life tracking routes: sleep, mood, exercise/water, finance."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import get_current_user_id, sleep_storage, mood_storage, health_storage, finance_storage
from ..models import SleepRecord, MoodRecord, HealthRecord, FinanceRecord

router = APIRouter()


# --- Sleep ---

class SleepCreate(BaseModel):
    record_date: str
    sleep_time: Optional[str] = None
    wake_time: Optional[str] = None
    duration_hours: float = 0.0
    quality: int = 3
    note: str = ""


@router.get("/api/sleep")
def get_sleep(start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    sd = date.fromisoformat(start) if start else None
    ed = date.fromisoformat(end) if end else None
    records = sleep_storage.get_by_user(user_id, sd, ed)
    return [r.to_dict() for r in records]


@router.post("/api/sleep")
def create_sleep(data: SleepCreate, user_id: str = Depends(get_current_user_id)):
    r = SleepRecord(user_id=user_id, record_date=date.fromisoformat(data.record_date))
    r.sleep_time = data.sleep_time
    r.wake_time = data.wake_time
    r.duration_hours = data.duration_hours
    r.quality = data.quality
    r.note = data.note
    sleep_storage.save(r)
    return r.to_dict()


@router.delete("/api/sleep/{record_id}")
def delete_sleep(record_id: str, user_id: str = Depends(get_current_user_id)):
    sleep_storage.delete(record_id)
    return {"ok": True}


# --- Mood ---

class MoodCreate(BaseModel):
    record_date: str
    mood: str = "neutral"
    energy: int = 3
    note: str = ""


@router.get("/api/mood")
def get_mood(start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    sd = date.fromisoformat(start) if start else None
    ed = date.fromisoformat(end) if end else None
    records = mood_storage.get_by_user(user_id, sd, ed)
    return [r.to_dict() for r in records]


@router.post("/api/mood")
def create_mood(data: MoodCreate, user_id: str = Depends(get_current_user_id)):
    r = MoodRecord(user_id=user_id, record_date=date.fromisoformat(data.record_date))
    r.mood = data.mood
    r.energy = data.energy
    r.note = data.note
    mood_storage.save(r)
    return r.to_dict()


@router.delete("/api/mood/{record_id}")
def delete_mood(record_id: str, user_id: str = Depends(get_current_user_id)):
    mood_storage.delete(record_id)
    return {"ok": True}


# --- Health (exercise, water, steps, weight) ---

class HealthCreate(BaseModel):
    record_date: str
    exercise_type: str = ""
    exercise_minutes: int = 0
    exercise_calories: int = 0
    water_ml: int = 0
    steps: int = 0
    weight_kg: float = 0.0
    note: str = ""


@router.get("/api/health")
def get_health(start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    sd = date.fromisoformat(start) if start else None
    ed = date.fromisoformat(end) if end else None
    records = health_storage.get_by_user(user_id, sd, ed)
    return [r.to_dict() for r in records]


@router.post("/api/health")
def create_health(data: HealthCreate, user_id: str = Depends(get_current_user_id)):
    r = HealthRecord(user_id=user_id, record_date=date.fromisoformat(data.record_date))
    r.exercise_type = data.exercise_type
    r.exercise_minutes = data.exercise_minutes
    r.exercise_calories = data.exercise_calories
    r.water_ml = data.water_ml
    r.steps = data.steps
    r.weight_kg = data.weight_kg
    r.note = data.note
    health_storage.save(r)
    return r.to_dict()


@router.delete("/api/health/{record_id}")
def delete_health(record_id: str, user_id: str = Depends(get_current_user_id)):
    health_storage.delete(record_id)
    return {"ok": True}


# --- Finance ---

class FinanceCreate(BaseModel):
    record_date: str
    amount: float = 0.0
    record_type: str = "expense"
    category: str = ""
    note: str = ""


@router.get("/api/finance")
def get_finance(start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    sd = date.fromisoformat(start) if start else None
    ed = date.fromisoformat(end) if end else None
    records = finance_storage.get_by_user(user_id, sd, ed)
    return [r.to_dict() for r in records]


@router.post("/api/finance")
def create_finance(data: FinanceCreate, user_id: str = Depends(get_current_user_id)):
    r = FinanceRecord(user_id=user_id, record_date=date.fromisoformat(data.record_date))
    r.amount = data.amount
    r.record_type = data.record_type
    r.category = data.category
    r.note = data.note
    finance_storage.save(r)
    return r.to_dict()


@router.delete("/api/finance/{record_id}")
def delete_finance(record_id: str, user_id: str = Depends(get_current_user_id)):
    finance_storage.delete(record_id)
    return {"ok": True}


@router.get("/api/finance/summary")
def finance_summary(start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    sd = date.fromisoformat(start) if start else None
    ed = date.fromisoformat(end) if end else None
    records = finance_storage.get_by_user(user_id, sd, ed)
    total_income = sum(r.amount for r in records if r.record_type == "income")
    total_expense = sum(r.amount for r in records if r.record_type == "expense")
    by_category = {}
    for r in records:
        if r.record_type == "expense":
            by_category[r.category or "其他"] = by_category.get(r.category or "其他", 0) + r.amount
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "by_category": by_category,
    }
