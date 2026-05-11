"""Dashboard routes for FastAPI."""

from datetime import date, datetime

from fastapi import APIRouter, Depends

from ..deps import (
    get_current_user_id,
    activity_storage,
    habit_storage,
    habit_record_storage,
    pomodoro_storage,
    goal_storage,
    goal_progress_storage,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(user_id: str = Depends(get_current_user_id)):
    today = date.today()
    today_str = today.isoformat()

    # Greeting based on time of day
    hour = datetime.now().hour
    if hour < 6:
        greeting = "夜深了，注意休息"
    elif hour < 12:
        greeting = "早上好，新的一天加油"
    elif hour < 18:
        greeting = "下午好，继续努力"
    else:
        greeting = "晚上好，辛苦了"

    # Activities
    all_activities = activity_storage.get_by_user(user_id)
    pending = 0
    in_progress = 0
    completed_today = 0
    today_activities = []
    recent_completed = []

    for a in all_activities:
        if a.status.value == "pending":
            pending += 1
        elif a.status.value == "in_progress":
            in_progress += 1

        # Today's activities: scheduled today and not completed/cancelled
        if a.scheduled_date == today and a.status.value in ("pending", "in_progress"):
            today_activities.append(a.to_dict())

        # Completed today
        if a.status.value == "completed" and a.completed_at and a.completed_at.date() == today:
            completed_today += 1

        # Recent completed (any date)
        if a.status.value == "completed":
            recent_completed.append(a)

    # Sort recent completed by completed_at desc, take 5
    recent_completed.sort(key=lambda x: x.completed_at or datetime.min, reverse=True)
    recent_completed = [a.to_dict() for a in recent_completed[:5]]

    # Pomodoro stats for today
    today_sessions = pomodoro_storage.get_by_user(user_id, filter_date=today)
    completed_sessions = [s for s in today_sessions if s.status == "completed"]
    pomodoro_count = len(completed_sessions)
    focus_minutes = sum(s.duration for s in completed_sessions)

    # Habits with today's checkin status
    habits = habit_storage.get_by_user(user_id)
    habits_data = []
    for h in habits:
        if not h.is_active:
            continue
        records = habit_record_storage.get_by_habit(h.id, start_date=today, end_date=today)
        checked_today = len(records) > 0
        hd = h.to_dict()
        hd["checked_today"] = checked_today
        habits_data.append(hd)

    # Goals with progress
    goals = goal_storage.get_by_user(user_id)
    goals_data = []
    for g in goals:
        progress_entries = goal_progress_storage.get_by_goal(g.id)
        current_value = sum(p.value for p in progress_entries)
        progress_pct = min(round((current_value / g.target_value) * 100, 1), 100) if g.target_value > 0 else 0
        gd = g.to_dict()
        gd["current_value"] = current_value
        gd["progress_pct"] = progress_pct
        goals_data.append(gd)

    return {
        "today": today_str,
        "greeting": greeting,
        "stats": {
            "pending": pending,
            "in_progress": in_progress,
            "completed_today": completed_today,
            "pomodoro_count": pomodoro_count,
            "focus_minutes": focus_minutes,
        },
        "today_activities": today_activities,
        "recent_completed": recent_completed,
        "habits": habits_data,
        "goals": goals_data,
    }
