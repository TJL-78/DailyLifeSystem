"""JSON file-based storage for activities and categories (with user_id support)."""

import json
import os
from typing import List, Optional
from datetime import date, time, datetime
from .models import Activity, ActivityStatus, ActivityPriority, RecurrenceType, Category


class JSONCategoryStorage:
    """JSON storage for categories."""

    def __init__(self, filepath: str = "categories.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, category: Category):
        cats = self._read_all()
        for i, c in enumerate(cats):
            if c["id"] == category.id:
                cats[i] = category.to_dict()
                self._write_all(cats)
                return
        cats.append(category.to_dict())
        self._write_all(cats)

    def get_by_user(self, user_id: str) -> List[Category]:
        cats = self._read_all()
        result = []
        for c in cats:
            if c["user_id"] == user_id:
                cat = Category(name=c["name"], user_id=c["user_id"], color=c.get("color", "#3498db"), icon=c.get("icon", ""))
                cat.id = c["id"]
                cat.sort_order = c.get("sort_order", 0)
                cat.created_at = datetime.fromisoformat(c["created_at"]) if c.get("created_at") else datetime.now()
                result.append(cat)
        result.sort(key=lambda x: (x.sort_order, x.name))
        return result

    def get(self, category_id: str) -> Optional[Category]:
        for c in self._read_all():
            if c["id"] == category_id:
                cat = Category(name=c["name"], user_id=c["user_id"], color=c.get("color", "#3498db"), icon=c.get("icon", ""))
                cat.id = c["id"]
                cat.sort_order = c.get("sort_order", 0)
                cat.created_at = datetime.fromisoformat(c["created_at"]) if c.get("created_at") else datetime.now()
                return cat
        return None

    def delete(self, category_id: str) -> bool:
        cats = self._read_all()
        filtered = [c for c in cats if c["id"] != category_id]
        if len(filtered) == len(cats):
            return False
        self._write_all(filtered)
        return True


class JSONActivityStorage:
    """JSON storage for activities with user_id support."""

    def __init__(self, filepath: str = "activities.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, activity: Activity):
        activities = self._read_all()
        d = activity.to_dict()
        for i, a in enumerate(activities):
            if a["id"] == activity.id:
                activities[i] = d
                self._write_all(activities)
                return
        activities.append(d)
        self._write_all(activities)

    def get(self, activity_id: str) -> Optional[Activity]:
        for a in self._read_all():
            if a["id"] == activity_id:
                return self._dict_to_activity(a)
        return None

    def get_by_user(self, user_id: str, status: str = None, priority: str = None,
                    category_id: str = None, scheduled_date: date = None) -> List[Activity]:
        result = []
        for a in self._read_all():
            if a.get("user_id") != user_id:
                continue
            if status and a.get("status") != status:
                continue
            if priority and a.get("priority") != priority:
                continue
            if category_id and a.get("category_id") != category_id:
                continue
            if scheduled_date and a.get("scheduled_date") != scheduled_date.isoformat():
                continue
            result.append(self._dict_to_activity(a))
        result.sort(key=lambda x: (x.sort_order, x.created_at), reverse=True)
        return result

    def delete(self, activity_id: str) -> bool:
        activities = self._read_all()
        filtered = [a for a in activities if a["id"] != activity_id]
        if len(filtered) == len(activities):
            return False
        self._write_all(filtered)
        return True

    def get_stats(self, user_id: str) -> dict:
        by_status = {}
        by_priority = {}
        for a in self._read_all():
            if a.get("user_id") != user_id:
                continue
            s = a.get("status", "pending")
            by_status[s] = by_status.get(s, 0) + 1
            p = a.get("priority", "medium")
            by_priority[p] = by_priority.get(p, 0) + 1
        return {"total": sum(by_status.values()), "by_status": by_status, "by_priority": by_priority}

    def _dict_to_activity(self, data: dict) -> Activity:
        a = Activity(
            title=data["title"],
            user_id=data.get("user_id", ""),
            description=data.get("description", ""),
            status=ActivityStatus(data.get("status", "pending")),
            priority=ActivityPriority(data.get("priority", "medium")),
            category_id=data.get("category_id"),
            duration_minutes=data.get("duration_minutes"),
            tags=data.get("tags", []),
            recurrence=RecurrenceType(data.get("recurrence", "none")),
            parent_id=data.get("parent_id"),
            sort_order=data.get("sort_order", 0),
        )
        a.id = data.get("id", a.id)
        if data.get("scheduled_date"):
            a.scheduled_date = date.fromisoformat(data["scheduled_date"])
        if data.get("scheduled_time"):
            a.scheduled_time = time.fromisoformat(data["scheduled_time"])
        if data.get("due_date"):
            a.due_date = date.fromisoformat(data["due_date"])
        if data.get("due_time"):
            a.due_time = time.fromisoformat(data["due_time"])
        if data.get("created_at"):
            a.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            a.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("completed_at"):
            a.completed_at = datetime.fromisoformat(data["completed_at"])
        if data.get("recurrence_end_date"):
            a.recurrence_end_date = date.fromisoformat(data["recurrence_end_date"])
        return a
