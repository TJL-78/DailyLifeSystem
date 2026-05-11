"""Goals routes for FastAPI."""

from datetime import date, datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..schemas import GoalCreateRequest, GoalUpdateRequest, GoalProgressRequest
from ..deps import get_current_user_id, goal_storage, goal_progress_storage
from ..models import Goal, GoalProgress

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("", status_code=201)
def create_goal(req: GoalCreateRequest, user_id: str = Depends(get_current_user_id)):
    if not req.title:
        return JSONResponse({"error": "title required"}, status_code=400)
    goal = Goal(
        title=req.title,
        user_id=user_id,
        description=req.description or "",
        target_value=req.target_value,
        unit=req.unit,
        period=req.period,
        category_id=req.category_id,
    )
    if req.start_date:
        goal.start_date = date.fromisoformat(req.start_date)
    if req.end_date:
        goal.end_date = date.fromisoformat(req.end_date)
    goal_storage.save(goal)
    return goal.to_dict()


@router.get("")
def list_goals(user_id: str = Depends(get_current_user_id)):
    goals = goal_storage.get_by_user(user_id)
    result = []
    for g in goals:
        d = g.to_dict()
        # Aggregate current_value from progress entries
        progress = goal_progress_storage.get_by_goal(g.id)
        d["current_value"] = sum(p.value for p in progress)
        result.append(d)
    return result


@router.put("/{goal_id}")
def update_goal(goal_id: str, req: GoalUpdateRequest, user_id: str = Depends(get_current_user_id)):
    goal = goal_storage.get(goal_id)
    if not goal or goal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.title is not None:
        goal.title = req.title
    if req.description is not None:
        goal.description = req.description
    if req.target_value is not None:
        goal.target_value = req.target_value
    if req.unit is not None:
        goal.unit = req.unit
    if req.period is not None:
        goal.period = req.period
    if req.category_id is not None:
        goal.category_id = req.category_id
    if req.start_date is not None:
        goal.start_date = date.fromisoformat(req.start_date)
    if req.end_date is not None:
        goal.end_date = date.fromisoformat(req.end_date)
    goal.updated_at = datetime.now()
    goal_storage.save(goal)
    return goal.to_dict()


@router.delete("/{goal_id}")
def delete_goal(goal_id: str, user_id: str = Depends(get_current_user_id)):
    goal = goal_storage.get(goal_id)
    if not goal or goal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    goal_progress_storage.delete_by_goal(goal_id)
    goal_storage.delete(goal_id)
    return {"message": "deleted"}


@router.post("/{goal_id}/progress", status_code=201)
def add_progress(goal_id: str, req: GoalProgressRequest, user_id: str = Depends(get_current_user_id)):
    goal = goal_storage.get(goal_id)
    if not goal or goal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    progress = GoalProgress(
        goal_id=goal_id,
        value=req.value,
        note=req.note or "",
        progress_date=date.fromisoformat(req.date) if req.date else date.today(),
    )
    goal_progress_storage.save(progress)
    return progress.to_dict()


@router.get("/{goal_id}/progress")
def list_progress(goal_id: str, user_id: str = Depends(get_current_user_id)):
    goal = goal_storage.get(goal_id)
    if not goal or goal.user_id != user_id:
        return JSONResponse({"error": "not found"}, status_code=404)
    entries = goal_progress_storage.get_by_goal(goal_id)
    return [p.to_dict() for p in entries]
