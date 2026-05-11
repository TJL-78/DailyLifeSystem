"""Activity routes for FastAPI."""

from datetime import date, time, datetime
from typing import List

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from ..schemas import ActivityCreateRequest, ActivityUpdateRequest, TemplateCreateRequest, TagUpdateRequest, ReorderRequest, ShareActivityRequest
from ..deps import get_current_user_id, activity_storage, template_storage, shared_activity_storage, user_storage
from ..models import Activity, ActivityPriority, RecurrenceType, ActivityTemplate, SharedActivity

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


# --- Feature 9: Drag & Sort (Reorder) --- must be before /{activity_id}

@router.put("/reorder")
def reorder_activities(req: ReorderRequest, user_id: str = Depends(get_current_user_id)):
    for idx, aid in enumerate(req.activity_ids):
        activity = activity_storage.get(aid)
        if activity and activity.user_id == user_id:
            activity.sort_order = idx
            activity.updated_at = datetime.now()
            activity_storage.save(activity)
    return {"message": "reordered"}


# --- Feature 11: shared list --- must be before /{activity_id}

@router.get("/shared")
def list_shared_activities(user_id: str = Depends(get_current_user_id)):
    shared_records = shared_activity_storage.get_shared_with_user(user_id)
    results = []
    for s in shared_records:
        activity = activity_storage.get(s.activity_id)
        if activity:
            d = activity.to_dict()
            d["shared_permission"] = s.permission
            d["shared_by"] = s.owner_id
            results.append(d)
    return results


@router.get("")
def list_activities(request: Request, status: str = None, priority: str = None,
                    category_id: str = None, today: str = None,
                    user_id: str = Depends(get_current_user_id)):
    today_only = bool(today and today not in ("0", "false", ""))
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


# --- Feature 5: Activity Templates ---

template_router = APIRouter(prefix="/api/templates", tags=["templates"])


@template_router.post("", status_code=201)
def create_template(req: TemplateCreateRequest, user_id: str = Depends(get_current_user_id)):
    if not req.title:
        return JSONResponse({"error": "title is required"}, status_code=400)
    template = ActivityTemplate(
        title=req.title,
        user_id=user_id,
        description=req.description or "",
        priority=req.priority or "medium",
        category_id=req.category_id,
        duration_minutes=req.duration_minutes,
        tags=req.tags or [],
    )
    template_storage.save(template)
    return template.to_dict()


@template_router.get("")
def list_templates(user_id: str = Depends(get_current_user_id)):
    templates = template_storage.get_by_user(user_id)
    return [t.to_dict() for t in templates]


@template_router.delete("/{template_id}")
def delete_template(template_id: str, user_id: str = Depends(get_current_user_id)):
    template = template_storage.get(template_id)
    if not template or template.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    template_storage.delete(template_id)
    return {"message": "deleted"}


@template_router.post("/{template_id}/use", status_code=201)
def use_template(template_id: str, user_id: str = Depends(get_current_user_id)):
    template = template_storage.get(template_id)
    if not template or template.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    activity = Activity(
        title=template.title,
        user_id=user_id,
        description=template.description,
        priority=ActivityPriority(template.priority or "medium"),
        category_id=template.category_id,
        duration_minutes=template.duration_minutes,
        tags=list(template.tags),
    )
    activity_storage.save(activity)
    return activity.to_dict()


# --- Feature 6: Tag Management ---

tag_router = APIRouter(prefix="/api/tags", tags=["tags"])


@tag_router.get("")
def list_tags(user_id: str = Depends(get_current_user_id)):
    activities = activity_storage.get_by_user(user_id)
    tag_counts: dict = {}
    for a in activities:
        for t in a.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    return [{"name": name, "count": count} for name, count in sorted(tag_counts.items())]


@tag_router.put("/{tag_name}")
def update_tag(tag_name: str, req: TagUpdateRequest, user_id: str = Depends(get_current_user_id)):
    activities = activity_storage.get_by_user(user_id)
    found = False
    for a in activities:
        if tag_name in a.tags:
            found = True
            if req.new_name:
                a.tags = [req.new_name if t == tag_name else t for t in a.tags]
                a.updated_at = datetime.now()
                activity_storage.save(a)
    if not found:
        return JSONResponse({"error": "tag not found"}, status_code=404)
    return {"message": "updated"}


@tag_router.delete("/{tag_name}")
def delete_tag(tag_name: str, user_id: str = Depends(get_current_user_id)):
    activities = activity_storage.get_by_user(user_id)
    found = False
    for a in activities:
        if tag_name in a.tags:
            found = True
            a.tags = [t for t in a.tags if t != tag_name]
            a.updated_at = datetime.now()
            activity_storage.save(a)
    if not found:
        return JSONResponse({"error": "tag not found"}, status_code=404)
    return {"message": "deleted"}


# --- Feature 11: Share/Unshare (path param endpoints) ---

@router.post("/{activity_id}/share")
def share_activity(activity_id: str, req: ShareActivityRequest, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.permission not in ("view", "edit"):
        return JSONResponse({"error": "permission must be 'view' or 'edit'"}, status_code=400)
    target_user = user_storage.get_by_username(req.username)
    if not target_user:
        return JSONResponse({"error": "user not found"}, status_code=404)
    if target_user.id == user_id:
        return JSONResponse({"error": "cannot share with yourself"}, status_code=400)
    existing = shared_activity_storage.find(activity_id, target_user.id)
    if existing:
        existing.permission = req.permission
        shared_activity_storage.save(existing)
        return existing.to_dict()
    shared = SharedActivity(
        activity_id=activity_id,
        owner_id=user_id,
        shared_with_id=target_user.id,
        permission=req.permission,
    )
    shared_activity_storage.save(shared)
    return shared.to_dict()


@router.delete("/{activity_id}/share/{target_user_id}")
def unshare_activity(activity_id: str, target_user_id: str, user_id: str = Depends(get_current_user_id)):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    deleted = shared_activity_storage.delete(activity_id, target_user_id)
    if not deleted:
        return JSONResponse({"error": "share not found"}, status_code=404)
    return {"message": "unshared"}
