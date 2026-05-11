"""Stats and export routes for FastAPI."""

import csv
import io
import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from ..deps import get_current_user_id, activity_storage, category_storage, habit_storage, habit_record_storage, pomodoro_storage, journal_storage, goal_storage, goal_progress_storage
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


@router.get("/api/stats/report")
def generate_report(type: str = "weekly", user_id: str = Depends(get_current_user_id)):
    """Generate a structured daily or weekly report from user data."""
    today_date = date.today()
    if type == "daily":
        start_date = today_date
        end_date = today_date
        date_range = today_date.isoformat()
    else:
        start_date = today_date - timedelta(days=today_date.weekday())
        end_date = start_date + timedelta(days=6)
        date_range = f"{start_date.isoformat()} ~ {end_date.isoformat()}"

    all_acts = activity_storage.get_by_user(user_id)
    period_acts = [a for a in all_acts if a.created_at.date() >= start_date and a.created_at.date() <= end_date]
    completed_acts = [a for a in period_acts if a.status == ActivityStatus.COMPLETED]
    total = len(period_acts)
    comp = len(completed_acts)
    rate = round(comp / total * 100, 1) if total > 0 else 0

    cats = category_storage.get_by_user(user_id)
    cat_map = {c.id: c.name for c in cats}
    cat_counts = {}
    for a in period_acts:
        cname = cat_map.get(a.category_id, "未分类") if a.category_id else "未分类"
        cat_counts[cname] = cat_counts.get(cname, 0) + 1

    # Time analysis from pomodoro
    all_sessions = pomodoro_storage.get_by_user(user_id)
    period_sessions = [s for s in all_sessions if s.status == "completed" and s.start_time.date() >= start_date and s.start_time.date() <= end_date]
    total_focus = sum(s.duration for s in period_sessions)
    avg_session = round(total_focus / len(period_sessions), 1) if period_sessions else 0

    # Time slot analysis
    hour_counts = {}
    for s in period_sessions:
        h = s.start_time.hour
        hour_counts[h] = hour_counts.get(h, 0) + 1
    most_productive = max(hour_counts, key=hour_counts.get) if hour_counts else None
    productive_str = f"{most_productive}:00-{most_productive+1}:00" if most_productive is not None else "N/A"

    # Habits
    habits = habit_storage.get_by_user(user_id)
    habits_maintained = 0
    streak_info = []
    for h in habits:
        records = habit_record_storage.get_by_habit(h.id, start_date, end_date)
        if records:
            habits_maintained += 1
            streak_info.append(f"{h.name}: {len(records)}天")

    # Journals
    journals = journal_storage.get_by_user(user_id)
    period_journals = [j for j in journals if j.journal_date >= start_date and j.journal_date <= end_date]
    moods = [j.mood for j in period_journals if j.mood]

    # Goals
    goals = goal_storage.get_by_user(user_id)
    goal_summaries = []
    for g in goals:
        progress_records = goal_progress_storage.get_by_goal(g.id)
        current = sum(p.value for p in progress_records) if progress_records else 0
        pct = round(current / g.target_value * 100, 1) if g.target_value else 0
        goal_summaries.append(f"{g.title}: {pct}%")

    # Build sections
    sections = []
    type_label = "日报" if type == "daily" else "周报"

    sections.append({
        "title": "活动概览",
        "content": f"本{'日' if type == 'daily' else '周'}创建 {total} 个活动，完成 {comp} 个，完成率 {rate}%。",
        "stats": {"总数": total, "已完成": comp, "完成率": f"{rate}%", **cat_counts}
    })

    sections.append({
        "title": "时间分析",
        "content": f"总专注 {total_focus} 分钟，共 {len(period_sessions)} 次番茄钟，平均每次 {avg_session} 分钟。最高效时段：{productive_str}。",
        "stats": {"总专注分钟": total_focus, "番茄钟次数": len(period_sessions), "平均时长": f"{avg_session}min", "高效时段": productive_str}
    })

    sections.append({
        "title": "习惯总结",
        "content": f"共 {len(habits)} 个习惯，本期坚持 {habits_maintained} 个。" + (" " + "、".join(streak_info) if streak_info else ""),
        "stats": {"总习惯": len(habits), "本期坚持": habits_maintained}
    })

    sections.append({
        "title": "日志概况",
        "content": f"记录 {len(period_journals)} 篇日志。" + (f" 心情关键词：{'、'.join(moods[:5])}" if moods else ""),
        "stats": {"日志数": len(period_journals)}
    })

    sections.append({
        "title": "目标进度",
        "content": "、".join(goal_summaries) if goal_summaries else "暂无活跃目标。",
        "stats": {"活跃目标": len(goals)}
    })

    # Recommendations
    recommendations = []
    if rate < 50 and total > 0:
        recommendations.append("完成率较低，建议适当减少任务数量或拆分大任务。")
    if total_focus < 60 and type == "weekly":
        recommendations.append("本周专注时间不足 1 小时，建议每天安排至少一个番茄钟。")
    if habits_maintained < len(habits) // 2 and len(habits) > 0:
        recommendations.append("部分习惯未坚持，建议设置提醒或减少习惯数量。")
    if len(period_journals) == 0:
        recommendations.append("本期未写日志，建议每天花几分钟记录心得。")
    if not recommendations:
        recommendations.append("各项数据表现良好，继续保持！")

    # Raw text
    raw_lines = [f"# {type_label}\n", f"日期范围：{date_range}\n"]
    for s in sections:
        raw_lines.append(f"\n## {s['title']}\n\n{s['content']}\n")
    if recommendations:
        raw_lines.append("\n## 建议\n")
        for r in recommendations:
            raw_lines.append(f"- {r}\n")
    raw_text = "".join(raw_lines)

    return {
        "type": type,
        "date_range": date_range,
        "sections": sections,
        "recommendations": recommendations,
        "raw_text": raw_text,
    }


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
