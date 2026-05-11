"""Activity routes for FastAPI."""

from datetime import date, time, datetime

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from ..schemas import ActivityCreateRequest, ActivityUpdateRequest
from ..deps import get_current_user_id, activity_storage
from ..models import Activity, ActivityPriority, RecurrenceType

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("/search")
def search_activities(request: Request, q: str = "", user_id: str = Depends(get_current_user_id)):
    q = q.strip()
    if not q:
        return []
    activities = activity_storage.get_by_user(user_id)
    q_lower = q.lower()
    results = [a for a in activities if q_lower in a.title.lower() or q_lower in a.description.lower() or any(q_lower in t.lower() for t in a.tags)]
    return [a.to_dict() for a in results]


@router.get("/calendar")
def calendar_activities(request: Request, start: str = None, end: str = None, user_id: str = Depends(get_current_user_id)):
    if not start or not end:
        return JSONResponse({"error": "start and end required"}, status_code=400)
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    all_activities = activity_storage.get_by_user(user_id)
    results = []
    for a in all_activities:
        d = a.scheduled_date or a.due_date
        if d and start_date <= d <= end_date:
            results.append(a)
    return [a.to_dict() for a in results]


@router.get("")
def list_activities(request: Request, status: str = None, priority: str = None,
                    category_id: str = None, today: str = None,
                    user_id: str = Depends(get_current_user_id)):
    today_only = (today or "").lower() == "true"
    scheduled_date = date.today() if today_only else None
    activities = activity_storage.get_by_user(
        user_id, status=status, priority=priority,
        category_id=category_id, scheduled_date=scheduled_date
    )
    return [a.to_dict() for a in activities]


@router.post("", status_code=201)
def create_activity(req: ActivityCreateRequest, request: Request, user_id: str = Depends(get_current_user_id)):
    if not req.title:
        return JSONResponse({"error": "title is required"}, status_code=400)
    activity = Activity(
        title=req.title,
        user_id=user_id,
        description=req.description or "",
        priority=ActivityPriority(req.priority or "medium"),
        category_id=req.category_id,
        scheduled_date=date.fromisoformat(req.scheduled_date) if req.scheduled_date else None,
        scheduled_time=time.fromisoformat(req.scheduled_time) if req.scheduled_time else None,
        due_date=date.fromisoformat(req.due_date) if req.due_date else None,
        due_time=time.fromisoformat(req.due_time) if req.due_time else None,
        duration_minutes=req.duration_minutes,
        tags=req.tags or [],
        recurrence=RecurrenceType(req.recurrence or "none"),
        parent_id=req.parent_id,
    )
    activity_storage.save(activity)
    return activity.to_dict()


@router.get("/{activity_id}")
def get_activity(activity_id: str, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    return activity.to_dict()


@router.put("/{activity_id}")
def update_activity(activity_id: str, req: ActivityUpdateRequest, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)

    if req.title is not None:
        activity.title = req.title
    if req.description is not None:
        activity.description = req.description
    if req.priority is not None:
        activity.priority = ActivityPriority(req.priority)
    if req.category_id is not None:
        activity.category_id = req.category_id or None
    if req.scheduled_date is not None:
        activity.scheduled_date = date.fromisoformat(req.scheduled_date) if req.scheduled_date else None
    if req.scheduled_time is not None:
        activity.scheduled_time = time.fromisoformat(req.scheduled_time) if req.scheduled_time else None
    if req.due_date is not None:
        activity.due_date = date.fromisoformat(req.due_date) if req.due_date else None
    if req.recurrence is not None:
        activity.recurrence = RecurrenceType(req.recurrence)
    if req.tags is not None:
        activity.tags = req.tags

    activity.updated_at = datetime.now()
    activity_storage.save(activity)
    return activity.to_dict()


@router.post("/{activity_id}/complete")
def complete_activity(activity_id: str, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    activity.complete()
    activity_storage.save(activity)
    return activity.to_dict()


@router.post("/{activity_id}/start")
def start_activity(activity_id: str, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    activity.start()
    activity_storage.save(activity)
    return activity.to_dict()


@router.post("/{activity_id}/cancel")
def cancel_activity(activity_id: str, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    activity.cancel()
    activity_storage.save(activity)
    return activity.to_dict()


@router.delete("/{activity_id}")
def delete_activity(activity_id: str, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    activity_storage.delete(activity_id)
    return {"message": "deleted"}


@router.get("/{activity_id}/subtasks")
def list_subtasks(activity_id: str, user_id: str = Depends(get_current_user_id)):
    parent = activity_storage.get(activity_id)
    if not parent or parent.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    all_activities = activity_storage.get_by_user(user_id)
    subtasks = [a for a in all_activities if a.parent_id == activity_id]
    return [a.to_dict() for a in subtasks]


@router.post("/{activity_id}/subtasks", status_code=201)
def create_subtask(activity_id: str, req: ActivityCreateRequest, user_id: str = Depends(get_current_user_id)):
    parent = activity_storage.get(activity_id)
    if not parent or parent.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if not req.title:
        return JSONResponse({"error": "title is required"}, status_code=400)
    subtask = Activity(
        title=req.title,
        user_id=user_id,
        description=req.description or "",
        priority=ActivityPriority(req.priority or parent.priority.value),
        category_id=parent.category_id,
        scheduled_date=parent.scheduled_date,
        parent_id=activity_id,
        tags=req.tags or [],
    )
    activity_storage.save(subtask)
    return subtask.to_dict()
