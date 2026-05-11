"""Backup & restore routes for FastAPI."""

import json
from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response, JSONResponse

from ..deps import (
    get_current_user_id, activity_storage, category_storage, habit_storage,
    habit_record_storage, journal_storage, journal_comment_storage,
    pomodoro_storage, goal_storage, goal_progress_storage, template_storage,
)
from ..models import (
    Activity, ActivityPriority, ActivityStatus, RecurrenceType, Category,
    Habit, HabitRecord, Journal, JournalComment, PomodoroSession,
    Goal, GoalProgress, ActivityTemplate,
)

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.get("/export")
def export_all(user_id: str = Depends(get_current_user_id)):
    data = {
        "activities": [a.to_dict() for a in activity_storage.get_by_user(user_id)],
        "categories": [c.to_dict() for c in category_storage.get_by_user(user_id)],
        "habits": [h.to_dict() for h in habit_storage.get_by_user(user_id)],
        "journals": [j.to_dict() for j in journal_storage.get_by_user(user_id)],
        "pomodoro_sessions": [s.to_dict() for s in pomodoro_storage.get_by_user(user_id)],
        "goals": [g.to_dict() for g in goal_storage.get_by_user(user_id)],
        "templates": [t.to_dict() for t in template_storage.get_by_user(user_id)],
    }
    # Gather habit records for user's habits
    records = []
    for h in habit_storage.get_by_user(user_id):
        records.extend([r.to_dict() for r in habit_record_storage.get_by_habit(h.id)])
    data["habit_records"] = records

    # Gather journal comments for user's journals
    comments = []
    for j in journal_storage.get_by_user(user_id):
        comments.extend([c.to_dict() for c in journal_comment_storage.get_by_journal(j.id)])
    data["journal_comments"] = comments

    # Gather goal progress for user's goals
    progress = []
    for g in goal_storage.get_by_user(user_id):
        progress.extend([p.to_dict() for p in goal_progress_storage.get_by_goal(g.id)])
    data["goal_progress"] = progress

    content = json.dumps(data, ensure_ascii=False, indent=2)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=backup.json"},
    )


@router.post("/import")
def import_all(request_data: dict, user_id: str = Depends(get_current_user_id)):
    imported = {}

    # Categories
    for c in request_data.get("categories", []):
        cat = Category(name=c["name"], user_id=user_id, color=c.get("color", "#3498db"), icon=c.get("icon", ""))
        cat.id = c.get("id", cat.id)
        cat.sort_order = c.get("sort_order", 0)
        category_storage.save(cat)
    imported["categories"] = len(request_data.get("categories", []))

    # Activities
    for a in request_data.get("activities", []):
        activity = Activity(
            title=a["title"], user_id=user_id,
            description=a.get("description", ""),
            status=ActivityStatus(a.get("status", "pending")),
            priority=ActivityPriority(a.get("priority", "medium")),
            category_id=a.get("category_id"),
            duration_minutes=a.get("duration_minutes"),
            tags=a.get("tags", []),
            recurrence=RecurrenceType(a.get("recurrence", "none")),
            parent_id=a.get("parent_id"),
            sort_order=a.get("sort_order", 0),
        )
        activity.id = a.get("id", activity.id)
        if a.get("scheduled_date"):
            activity.scheduled_date = date.fromisoformat(a["scheduled_date"])
        if a.get("due_date"):
            activity.due_date = date.fromisoformat(a["due_date"])
        if a.get("completed_at"):
            activity.completed_at = datetime.fromisoformat(a["completed_at"])
        activity_storage.save(activity)
    imported["activities"] = len(request_data.get("activities", []))

    # Habits
    for h in request_data.get("habits", []):
        habit = Habit(name=h["name"], user_id=user_id, description=h.get("description", ""),
                      frequency=h.get("frequency", "daily"), target_count=h.get("target_count", 1),
                      color=h.get("color", "#27ae60"), is_active=h.get("is_active", True))
        habit.id = h.get("id", habit.id)
        habit_storage.save(habit)
    imported["habits"] = len(request_data.get("habits", []))

    # Habit records
    for r in request_data.get("habit_records", []):
        rec = HabitRecord(habit_id=r["habit_id"], record_date=date.fromisoformat(r["record_date"]),
                          count=r.get("count", 1), note=r.get("note", ""))
        rec.id = r.get("id", rec.id)
        habit_record_storage.save(rec)
    imported["habit_records"] = len(request_data.get("habit_records", []))

    # Journals
    for j in request_data.get("journals", []):
        journal = Journal(user_id=user_id, journal_date=date.fromisoformat(j["journal_date"]),
                          content=j.get("content", ""), weather=j.get("weather", ""),
                          mood=j.get("mood", ""), images=j.get("images", []))
        journal.id = j.get("id", journal.id)
        journal_storage.save(journal)
    imported["journals"] = len(request_data.get("journals", []))

    # Journal comments
    for c in request_data.get("journal_comments", []):
        comment = JournalComment(journal_id=c["journal_id"], user_id=user_id, content=c.get("content", ""))
        comment.id = c.get("id", comment.id)
        journal_comment_storage.save(comment)
    imported["journal_comments"] = len(request_data.get("journal_comments", []))

    # Goals
    for g in request_data.get("goals", []):
        goal = Goal(title=g["title"], user_id=user_id, description=g.get("description", ""),
                    target_value=g.get("target_value", 1), unit=g.get("unit", ""),
                    period=g.get("period", "weekly"), category_id=g.get("category_id"))
        goal.id = g.get("id", goal.id)
        if g.get("start_date"):
            goal.start_date = date.fromisoformat(g["start_date"])
        if g.get("end_date"):
            goal.end_date = date.fromisoformat(g["end_date"])
        goal_storage.save(goal)
    imported["goals"] = len(request_data.get("goals", []))

    # Goal progress
    for p in request_data.get("goal_progress", []):
        gp = GoalProgress(goal_id=p["goal_id"], value=p.get("value", 0), note=p.get("note", ""),
                          progress_date=date.fromisoformat(p["progress_date"]) if p.get("progress_date") else date.today())
        gp.id = p.get("id", gp.id)
        goal_progress_storage.save(gp)
    imported["goal_progress"] = len(request_data.get("goal_progress", []))

    # Pomodoro sessions
    for s in request_data.get("pomodoro_sessions", []):
        session = PomodoroSession(user_id=user_id, duration=s.get("duration", 25),
                                  activity_id=s.get("activity_id"), label=s.get("label"),
                                  status=s.get("status", "completed"))
        session.id = s.get("id", session.id)
        if s.get("start_time"):
            session.start_time = datetime.fromisoformat(s["start_time"])
        if s.get("end_time"):
            session.end_time = datetime.fromisoformat(s["end_time"])
        pomodoro_storage.save(session)
    imported["pomodoro_sessions"] = len(request_data.get("pomodoro_sessions", []))

    # Templates
    for t in request_data.get("templates", []):
        tmpl = ActivityTemplate(title=t["title"], user_id=user_id, description=t.get("description", ""),
                                priority=t.get("priority", "medium"), category_id=t.get("category_id"),
                                duration_minutes=t.get("duration_minutes"), tags=t.get("tags", []))
        tmpl.id = t.get("id", tmpl.id)
        template_storage.save(tmpl)
    imported["templates"] = len(request_data.get("templates", []))

    return {"message": "import completed", "imported": imported}
