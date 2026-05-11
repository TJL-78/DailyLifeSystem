"""Stats and export routes for FastAPI."""

import csv
import io
import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from ..deps import get_current_user_id, activity_storage, category_storage, habit_storage
from ..models import ActivityStatus

router = APIRouter(tags=["stats"])


@router.get("/api/stats")
def get_stats(user_id: str = Depends(get_current_user_id)):
    raw = activity_storage.get_stats(user_id)
    # Flatten by_status into top-level keys for Dashboard.vue
    by_status = raw.get("by_status", {})
    raw["pending"] = by_status.get("pending", 0)
    raw["in_progress"] = by_status.get("in_progress", 0)
    raw["completed"] = by_status.get("completed", 0)
    return raw


@router.get("/api/stats/detailed")
def get_detailed_stats(user_id: str = Depends(get_current_user_id)):
    all_acts = activity_storage.get_by_user(user_id)
    cats = category_storage.get_by_user(user_id)
    cat_map = {c.id: c.to_dict() for c in cats}

    by_category = {}
    for a in all_acts:
        cname = cat_map.get(a.category_id, {}).get("name", "未分类") if a.category_id else "未分类"
        by_category[cname] = by_category.get(cname, 0) + 1

    today = date.today()
    weekly = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7 * i)
        week_end = week_start + timedelta(days=6)
        created = len([a for a in all_acts if a.created_at.date() >= week_start and a.created_at.date() <= week_end])
        completed = len([a for a in all_acts if a.completed_at and a.completed_at.date() >= week_start and a.completed_at.date() <= week_end])
        weekly.append({"week": week_start.isoformat(), "new_count": created, "completed_count": completed})

    total_minutes = sum(a.duration_minutes or 0 for a in all_acts if a.status == ActivityStatus.COMPLETED)

    category_time = {}
    for a in all_acts:
        if not (a.duration_minutes and a.duration_minutes > 0):
            continue
        cname = cat_map.get(a.category_id, {}).get("name", "未分类") if a.category_id else "未分类"
        ccolor = cat_map.get(a.category_id, {}).get("color", "#95a5a6") if a.category_id else "#95a5a6"
        if cname not in category_time:
            category_time[cname] = {"name": cname, "color": ccolor, "total_minutes": 0, "tasks": []}
        category_time[cname]["total_minutes"] += a.duration_minutes
        category_time[cname]["tasks"].append({
            "title": a.title,
            "minutes": a.duration_minutes,
            "status": a.status.value,
        })

    return {
        "category_distribution": by_category,
        "weekly_trend": weekly,
        "total_completed_minutes": total_minutes,
        "total_time": total_minutes,
        "total": len(all_acts),
        "total_completed": len([a for a in all_acts if a.status == ActivityStatus.COMPLETED]),
        "completed": len([a for a in all_acts if a.status == ActivityStatus.COMPLETED]),
        "pending": len([a for a in all_acts if a.status == ActivityStatus.PENDING]),
        "category_time": {ct["name"]: ct["total_minutes"] for ct in category_time.values()},
    }


@router.get("/api/export/json")
def export_json(user_id: str = Depends(get_current_user_id)):
    activities = [a.to_dict() for a in activity_storage.get_by_user(user_id)]
    cats = [c.to_dict() for c in category_storage.get_by_user(user_id)]
    habits = [h.to_dict() for h in habit_storage.get_by_user(user_id)]
    data = json.dumps({"activities": activities, "categories": cats, "habits": habits}, ensure_ascii=False, indent=2)
    return Response(content=data, media_type="application/json",
                    headers={"Content-Disposition": "attachment; filename=daily_life_export.json"})


@router.get("/api/export/csv")
def export_csv(user_id: str = Depends(get_current_user_id)):
    activities = activity_storage.get_by_user(user_id)
    cats = {c.id: c.name for c in category_storage.get_by_user(user_id)}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["标题", "描述", "状态", "优先级", "分类", "计划日期", "计划时间", "时长(分)", "标签", "创建时间", "完成时间"])
    for a in activities:
        writer.writerow([
            a.title, a.description, a.status.value, a.priority.value,
            cats.get(a.category_id, ""), a.scheduled_date or "", a.scheduled_time or "",
            a.duration_minutes or "", ",".join(a.tags), a.created_at.isoformat(),
            a.completed_at.isoformat() if a.completed_at else "",
        ])
    output.seek(0)
    return Response(content=output.getvalue(), media_type="text/csv; charset=utf-8-sig",
                    headers={"Content-Disposition": "attachment; filename=activities.csv"})
