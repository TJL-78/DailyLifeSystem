"""Habit routes for FastAPI."""

from datetime import date

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from ..schemas import HabitCreateRequest, HabitUpdateRequest, HabitCheckinRequest
from ..deps import get_current_user_id, habit_storage, habit_record_storage
from ..models import Habit, HabitRecord

router = APIRouter(prefix="/api/habits", tags=["habits"])


@router.get("")
def list_habits(user_id: str = Depends(get_current_user_id)):
    habits = habit_storage.get_by_user(user_id)
    return [h.to_dict() for h in habits]


@router.post("", status_code=201)
def create_habit(req: HabitCreateRequest, user_id: str = Depends(get_current_user_id)):
    if not req.name:
        return JSONResponse({"error": "name required"}, status_code=400)
    habit = Habit(
        name=req.name,
        user_id=user_id,
        description=req.description or "",
        frequency=req.frequency or "daily",
        target_count=req.target_count or 1,
        color=req.color or "#27ae60",
    )
    habit_storage.save(habit)
    return habit.to_dict()


@router.put("/{habit_id}")
def update_habit(habit_id: str, req: HabitUpdateRequest, user_id: str = Depends(get_current_user_id)):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.name is not None:
        habit.name = req.name
    if req.description is not None:
        habit.description = req.description
    if req.frequency is not None:
        habit.frequency = req.frequency
    if req.target_count is not None:
        habit.target_count = req.target_count
    if req.color is not None:
        habit.color = req.color
    if req.is_active is not None:
        habit.is_active = req.is_active
    habit_storage.save(habit)
    return habit.to_dict()


@router.delete("/{habit_id}")
def delete_habit(habit_id: str, user_id: str = Depends(get_current_user_id)):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    habit_record_storage.delete_by_habit(habit_id)
    habit_storage.delete(habit_id)
    return {"message": "deleted"}


@router.post("/{habit_id}/checkin", status_code=201)
def checkin_habit(habit_id: str, req: HabitCheckinRequest = None, user_id: str = Depends(get_current_user_id)):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req is None:
        req = HabitCheckinRequest()
    record_date = date.fromisoformat(req.date) if req.date else date.today()
    record = HabitRecord(habit_id=habit_id, record_date=record_date, count=req.count or 1, note=req.note or "")
    habit_record_storage.save(record)
    return record.to_dict()


@router.post("/{habit_id}/uncheckin")
def uncheckin_habit(habit_id: str, req: HabitCheckinRequest = None, user_id: str = Depends(get_current_user_id)):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req is None:
        req = HabitCheckinRequest()
    record_date = date.fromisoformat(req.date) if req.date else date.today()
    habit_record_storage.delete_record(habit_id, record_date)
    return {"message": "unchecked"}


@router.get("/{habit_id}/records")
def habit_records(habit_id: str, start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    start_date = date.fromisoformat(start) if start else None
    end_date = date.fromisoformat(end) if end else None
    records = habit_record_storage.get_by_habit(habit_id, start_date, end_date)
    return [r.to_dict() for r in records]
