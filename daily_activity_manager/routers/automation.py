"""Efficiency & Automation routes: smart suggestions, automation rules, time blocks."""

from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import (
    get_current_user_id,
    activity_storage,
    habit_storage,
    habit_record_storage,
    pomodoro_storage,
    automation_rule_storage,
    time_block_storage,
)
from ..models import AutomationRule, TimeBlock

router = APIRouter()


# ─── Smart Suggestions ───────────────────────────────────────────────

@router.get("/api/suggestions")
def get_smart_suggestions(user_id: str = Depends(get_current_user_id)):
    """Analyse user history and suggest today's priority tasks."""
    today = date.today()
    now_hour = datetime.now().hour

    suggestions = []

    # 1. Overdue / pending activities sorted by priority
    all_acts = activity_storage.get_by_user(user_id)
    overdue = []
    today_pending = []
    for a in all_acts:
        if a.status.value in ("completed", "cancelled"):
            continue
        if a.scheduled_date and a.scheduled_date < today:
            overdue.append(a)
        elif a.scheduled_date == today:
            today_pending.append(a)

    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    overdue.sort(key=lambda x: priority_order.get(x.priority.value, 9))
    today_pending.sort(key=lambda x: priority_order.get(x.priority.value, 9))

    for a in overdue[:3]:
        suggestions.append({
            "type": "overdue",
            "icon": "⚠",
            "text": f"逾期任务：{a.title}",
            "text_en": f"Overdue: {a.title}",
            "activity_id": a.id,
        })

    for a in today_pending[:3]:
        suggestions.append({
            "type": "today_priority",
            "icon": "📌",
            "text": f"今日优先：{a.title}",
            "text_en": f"Today priority: {a.title}",
            "activity_id": a.id,
        })

    # 2. Habits not checked in today
    habits = habit_storage.get_by_user(user_id)
    for h in habits:
        if not h.is_active:
            continue
        records = habit_record_storage.get_by_habit(h.id, start_date=today, end_date=today)
        if not records:
            suggestions.append({
                "type": "habit_reminder",
                "icon": "★",
                "text": f"习惯提醒：{h.name} 今日未打卡",
                "text_en": f"Habit reminder: {h.name} not checked in today",
                "habit_id": h.id,
            })

    # 3. Pomodoro suggestion based on time of day
    today_sessions = pomodoro_storage.get_by_user(user_id, filter_date=today)
    completed_count = len([s for s in today_sessions if s.status == "completed"])
    if completed_count == 0 and 8 <= now_hour <= 20:
        suggestions.append({
            "type": "pomodoro_suggest",
            "icon": "⏱",
            "text": "今天还没有专注记录，试试番茄钟？",
            "text_en": "No focus sessions today. Try a Pomodoro?",
        })
    elif completed_count >= 4:
        suggestions.append({
            "type": "break_suggest",
            "icon": "☕",
            "text": f"已完成 {completed_count} 次专注，适当休息一下",
            "text_en": f"Completed {completed_count} sessions, take a break",
        })

    # 4. Evening wind-down
    if now_hour >= 21:
        suggestions.append({
            "type": "evening",
            "icon": "🌙",
            "text": "夜间时段，适合整理日志和回顾",
            "text_en": "Evening time, good for journaling and review",
        })

    return suggestions[:8]


# ─── Automation Rules ────────────────────────────────────────────────

class RuleCreate(BaseModel):
    name: str
    trigger_type: str = "pomodoro_count"
    trigger_value: str = "3"
    action_type: str = "checkin_habit"
    action_value: str = ""
    is_active: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_value: Optional[str] = None
    action_type: Optional[str] = None
    action_value: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/api/automation/rules")
def list_rules(user_id: str = Depends(get_current_user_id)):
    rules = automation_rule_storage.get_by_user(user_id)
    return [r.to_dict() for r in rules]


@router.post("/api/automation/rules")
def create_rule(data: RuleCreate, user_id: str = Depends(get_current_user_id)):
    rule = AutomationRule(
        user_id=user_id,
        name=data.name,
        trigger_type=data.trigger_type,
        trigger_value=data.trigger_value,
        action_type=data.action_type,
        action_value=data.action_value,
        is_active=data.is_active,
    )
    automation_rule_storage.save(rule)
    return rule.to_dict()


@router.put("/api/automation/rules/{rule_id}")
def update_rule(rule_id: str, data: RuleUpdate, user_id: str = Depends(get_current_user_id)):
    rules = automation_rule_storage.get_by_user(user_id)
    target = None
    for r in rules:
        if r.id == rule_id:
            target = r
            break
    if not target:
        return {"error": "Rule not found"}
    if data.name is not None:
        target.name = data.name
    if data.trigger_type is not None:
        target.trigger_type = data.trigger_type
    if data.trigger_value is not None:
        target.trigger_value = data.trigger_value
    if data.action_type is not None:
        target.action_type = data.action_type
    if data.action_value is not None:
        target.action_value = data.action_value
    if data.is_active is not None:
        target.is_active = data.is_active
    automation_rule_storage.save(target)
    return target.to_dict()


@router.delete("/api/automation/rules/{rule_id}")
def delete_rule(rule_id: str, user_id: str = Depends(get_current_user_id)):
    automation_rule_storage.delete(rule_id)
    return {"ok": True}


# ─── Automation Rule Execution (check & fire) ────────────────────────

@router.post("/api/automation/check")
def check_automation_rules(user_id: str = Depends(get_current_user_id)):
    """Check all active rules and execute matching ones. Called by frontend after events."""
    today = date.today()
    rules = automation_rule_storage.get_by_user(user_id)
    fired = []

    for rule in rules:
        if not rule.is_active:
            continue

        matched = False
        if rule.trigger_type == "pomodoro_count":
            sessions = pomodoro_storage.get_by_user(user_id, filter_date=today)
            completed = len([s for s in sessions if s.status == "completed"])
            try:
                threshold = int(rule.trigger_value)
            except ValueError:
                threshold = 3
            if completed >= threshold:
                matched = True

        elif rule.trigger_type == "activity_complete":
            all_acts = activity_storage.get_by_user(user_id)
            completed_today = [
                a for a in all_acts
                if a.status.value == "completed" and a.completed_at and a.completed_at.date() == today
            ]
            try:
                threshold = int(rule.trigger_value)
            except ValueError:
                threshold = 1
            if len(completed_today) >= threshold:
                matched = True

        if matched:
            result = _execute_action(rule, user_id, today)
            if result:
                fired.append({"rule_id": rule.id, "rule_name": rule.name, "action": result})

    return {"fired": fired}


def _execute_action(rule: AutomationRule, user_id: str, today: date) -> Optional[str]:
    if rule.action_type == "checkin_habit" and rule.action_value:
        # Check if already checked in today
        records = habit_record_storage.get_by_habit(rule.action_value, start_date=today, end_date=today)
        if not records:
            from ..models import HabitRecord
            record = HabitRecord(habit_id=rule.action_value, user_id=user_id)
            habit_record_storage.save(record)
            return f"Auto checked-in habit"
    elif rule.action_type == "send_notification":
        return f"Notification: {rule.action_value}"
    return None


# ─── Time Blocks ─────────────────────────────────────────────────────

class TimeBlockCreate(BaseModel):
    block_date: str
    start_time: str
    end_time: str
    title: str = ""
    color: str = "#4f46e5"
    category: str = ""


class TimeBlockUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    title: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None


@router.get("/api/timeblocks")
def list_time_blocks(date_str: str = None, user_id: str = Depends(get_current_user_id)):
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    blocks = time_block_storage.get_by_user(user_id, target_date)
    return [b.to_dict() for b in blocks]


@router.post("/api/timeblocks")
def create_time_block(data: TimeBlockCreate, user_id: str = Depends(get_current_user_id)):
    block = TimeBlock(
        user_id=user_id,
        block_date=date.fromisoformat(data.block_date),
        start_time=data.start_time,
        end_time=data.end_time,
        title=data.title,
        color=data.color,
        category=data.category,
    )
    time_block_storage.save(block)
    return block.to_dict()


@router.put("/api/timeblocks/{block_id}")
def update_time_block(block_id: str, data: TimeBlockUpdate, user_id: str = Depends(get_current_user_id)):
    blocks = time_block_storage.get_by_user(user_id)
    target = None
    for b in blocks:
        if b.id == block_id:
            target = b
            break
    if not target:
        return {"error": "Time block not found"}
    if data.start_time is not None:
        target.start_time = data.start_time
    if data.end_time is not None:
        target.end_time = data.end_time
    if data.title is not None:
        target.title = data.title
    if data.color is not None:
        target.color = data.color
    if data.category is not None:
        target.category = data.category
    time_block_storage.save(target)
    return target.to_dict()


@router.delete("/api/timeblocks/{block_id}")
def delete_time_block(block_id: str, user_id: str = Depends(get_current_user_id)):
    time_block_storage.delete(block_id)
    return {"ok": True}
