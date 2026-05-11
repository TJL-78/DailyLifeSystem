"""Stats and export routes for FastAPI."""

import csv
import io
import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from ..deps import get_current_user_id, activity_storage, category_storage, habit_storage, habit_record_storage, pomodoro_storage, journal_storage
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
        "category_time_detail": list(category_time.values()),
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


@router.get("/api/stats/heatmap")
def get_heatmap(year: int = None, user_id: str = Depends(get_current_user_id)):
    if year is None:
        year = date.today().year
    dates = {}
    # Count completed activities
    all_acts = activity_storage.get_by_user(user_id)
    for a in all_acts:
        if a.completed_at and a.completed_at.year == year:
            d = a.completed_at.date().isoformat()
            dates[d] = dates.get(d, 0) + 1
    # Count habit checkins
    habits = habit_storage.get_by_user(user_id)
    for h in habits:
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        records = habit_record_storage.get_by_habit(h.id, start, end)
        for r in records:
            d = r.record_date.isoformat()
            dates[d] = dates.get(d, 0) + 1
    return {"dates": dates}


@router.get("/api/stats/monthly-report")
def get_monthly_report(year: int, month: int, user_id: str = Depends(get_current_user_id)):
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, last_day)

    all_acts = activity_storage.get_by_user(user_id)
    cats = category_storage.get_by_user(user_id)
    cat_map = {c.id: c.name for c in cats}

    # Filter activities for the month (by created_at or completed_at)
    month_acts = [a for a in all_acts if a.created_at.date() >= month_start and a.created_at.date() <= month_end]
    completed = [a for a in month_acts if a.status == ActivityStatus.COMPLETED]
    total = len(month_acts)
    completion_rate = round(len(completed) / total * 100, 1) if total > 0 else 0

    # Most active category
    cat_counts = {}
    for a in month_acts:
        cname = cat_map.get(a.category_id, "未分类") if a.category_id else "未分类"
        cat_counts[cname] = cat_counts.get(cname, 0) + 1
    most_active_category = max(cat_counts, key=cat_counts.get) if cat_counts else ""

    # Focus minutes from pomodoro
    all_sessions = pomodoro_storage.get_by_user(user_id)
    focus_sessions = [s for s in all_sessions if s.status == "completed" and s.start_time.date() >= month_start and s.start_time.date() <= month_end]
    total_focus_minutes = sum(s.duration for s in focus_sessions)

    # Habits maintained
    habits = habit_storage.get_by_user(user_id)
    habits_maintained = 0
    for h in habits:
        records = habit_record_storage.get_by_habit(h.id, month_start, month_end)
        if len(records) > 0:
            habits_maintained += 1

    # Journal count
    journals = journal_storage.get_by_user(user_id)
    journal_count = len([j for j in journals if j.journal_date >= month_start and j.journal_date <= month_end])

    # Top activities by duration
    top_activities = sorted(
        [{"title": a.title, "duration": a.duration_minutes or 0} for a in completed if a.duration_minutes],
        key=lambda x: x["duration"], reverse=True
    )[:10]

    return {
        "total_activities": total,
        "completed": len(completed),
        "completion_rate": completion_rate,
        "most_active_category": most_active_category,
        "total_focus_minutes": total_focus_minutes,
        "habits_maintained": habits_maintained,
        "journal_count": journal_count,
        "top_activities": top_activities,
    }
