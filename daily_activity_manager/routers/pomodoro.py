"""Pomodoro/Focus Timer routes for FastAPI."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..schemas import PomodoroStartRequest
from ..deps import get_current_user_id, pomodoro_storage, activity_storage
from ..models import PomodoroSession

router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])


@router.post("/sessions", status_code=201)
def start_session(req: PomodoroStartRequest, user_id: str = Depends(get_current_user_id)):
    session = PomodoroSession(
        user_id=user_id,
        duration=req.duration or 25,
        activity_id=req.activity_id,
        label=req.label,
        status="active",
    )
    pomodoro_storage.save(session)
    return session.to_dict()


@router.post("/sessions/{session_id}/complete")
def complete_session(session_id: str, user_id: str = Depends(get_current_user_id)):
    session = pomodoro_storage.get(session_id)
    if not session or session.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if session.status != "active":
        return JSONResponse({"error": "session is not active"}, status_code=400)
    session.status = "completed"
    session.end_time = datetime.now()
    pomodoro_storage.save(session)
    # Add duration to linked activity if present
    if session.activity_id:
        activity = activity_storage.get(session.activity_id)
        if activity and activity.user_id == user_id:
            activity.duration_minutes = (activity.duration_minutes or 0) + session.duration
            activity.updated_at = datetime.now()
            activity_storage.save(activity)
    return session.to_dict()


@router.post("/sessions/{session_id}/cancel")
def cancel_session(session_id: str, user_id: str = Depends(get_current_user_id)):
    session = pomodoro_storage.get(session_id)
    if not session or session.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    session.status = "cancelled"
    session.end_time = datetime.now()
    pomodoro_storage.save(session)
    return session.to_dict()


@router.get("/sessions")
def list_sessions(date: str = None, user_id: str = Depends(get_current_user_id)):
    from datetime import date as date_type
    filter_date = date_type.fromisoformat(date) if date else None
    sessions = pomodoro_storage.get_by_user(user_id, filter_date)
    return [s.to_dict() for s in sessions]


@router.get("/stats")
def pomodoro_stats(user_id: str = Depends(get_current_user_id)):
    all_sessions = pomodoro_storage.get_by_user(user_id)
    completed = [s for s in all_sessions if s.status == "completed"]

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    today_sessions = [s for s in completed if s.start_time.date() == today]
    week_sessions = [s for s in completed if s.start_time.date() >= week_start]

    return {
        "today_sessions": len(today_sessions),
        "today_minutes": sum(s.duration for s in today_sessions),
        "week_sessions": len(week_sessions),
        "week_minutes": sum(s.duration for s in week_sessions),
        "total_sessions": len(completed),
        "total_minutes": sum(s.duration for s in completed),
    }
