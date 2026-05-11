"""JSON file-based storage for activities and categories (with user_id support)."""

import json
import os
from typing import List, Optional
from datetime import date, time, datetime
from .models import Activity, ActivityStatus, ActivityPriority, RecurrenceType, Category, Habit, HabitRecord, Journal, JournalComment, PomodoroSession, Goal, GoalProgress, ActivityTemplate, SharedActivity


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


class JSONHabitStorage:
    """JSON storage for habits."""

    def __init__(self, filepath: str = "habits.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, habit: Habit):
        habits = self._read_all()
        d = habit.to_dict()
        d["is_active"] = habit.is_active
        for i, h in enumerate(habits):
            if h["id"] == habit.id:
                habits[i] = d
                self._write_all(habits)
                return
        habits.append(d)
        self._write_all(habits)

    def get_by_user(self, user_id: str) -> List[Habit]:
        result = []
        for h in self._read_all():
            if h.get("user_id") == user_id:
                habit = Habit(name=h["name"], user_id=h["user_id"], description=h.get("description", ""),
                              frequency=h.get("frequency", "daily"), target_count=h.get("target_count", 1),
                              color=h.get("color", "#27ae60"), is_active=h.get("is_active", True))
                habit.id = h["id"]
                habit.created_at = datetime.fromisoformat(h["created_at"]) if h.get("created_at") else datetime.now()
                result.append(habit)
        return result

    def get(self, habit_id: str) -> Optional[Habit]:
        for h in self._read_all():
            if h["id"] == habit_id:
                habit = Habit(name=h["name"], user_id=h["user_id"], description=h.get("description", ""),
                              frequency=h.get("frequency", "daily"), target_count=h.get("target_count", 1),
                              color=h.get("color", "#27ae60"), is_active=h.get("is_active", True))
                habit.id = h["id"]
                habit.created_at = datetime.fromisoformat(h["created_at"]) if h.get("created_at") else datetime.now()
                return habit
        return None

    def delete(self, habit_id: str) -> bool:
        habits = self._read_all()
        filtered = [h for h in habits if h["id"] != habit_id]
        if len(filtered) == len(habits):
            return False
        self._write_all(filtered)
        return True


class JSONHabitRecordStorage:
    """JSON storage for habit records."""

    def __init__(self, filepath: str = "habit_records.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, record: HabitRecord):
        records = self._read_all()
        d = record.to_dict()
        # Upsert by habit_id + record_date
        for i, r in enumerate(records):
            if r["habit_id"] == record.habit_id and r["record_date"] == record.record_date.isoformat():
                records[i] = d
                self._write_all(records)
                return
        records.append(d)
        self._write_all(records)

    def get_by_habit(self, habit_id: str, start_date: date = None, end_date: date = None) -> List[HabitRecord]:
        result = []
        for r in self._read_all():
            if r["habit_id"] != habit_id:
                continue
            rd = date.fromisoformat(r["record_date"])
            if start_date and rd < start_date:
                continue
            if end_date and rd > end_date:
                continue
            rec = HabitRecord(habit_id=r["habit_id"], record_date=rd, count=r.get("count", 1), note=r.get("note", ""))
            rec.id = r["id"]
            rec.created_at = datetime.fromisoformat(r["created_at"]) if r.get("created_at") else datetime.now()
            result.append(rec)
        return result

    def delete_by_habit(self, habit_id: str):
        records = self._read_all()
        self._write_all([r for r in records if r["habit_id"] != habit_id])

    def delete_record(self, habit_id: str, record_date: date) -> bool:
        records = self._read_all()
        filtered = [r for r in records if not (r["habit_id"] == habit_id and r["record_date"] == record_date.isoformat())]
        if len(filtered) == len(records):
            return False
        self._write_all(filtered)
        return True


class JSONJournalStorage:
    """JSON storage for daily journals."""

    def __init__(self, filepath: str = "journals.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, journal: Journal):
        items = self._read_all()
        for i, j in enumerate(items):
            if j["id"] == journal.id:
                items[i] = journal.to_dict()
                self._write_all(items)
                return
        items.append(journal.to_dict())
        self._write_all(items)

    def get(self, journal_id: str) -> Optional[Journal]:
        for j in self._read_all():
            if j["id"] == journal_id:
                return self._from_dict(j)
        return None

    def get_by_user(self, user_id: str) -> List[Journal]:
        result = []
        for j in self._read_all():
            if j["user_id"] == user_id:
                result.append(self._from_dict(j))
        result.sort(key=lambda x: x.journal_date, reverse=True)
        return result

    def get_by_date(self, user_id: str, journal_date: date) -> Optional[Journal]:
        for j in self._read_all():
            if j["user_id"] == user_id and j["journal_date"] == journal_date.isoformat():
                return self._from_dict(j)
        return None

    def delete(self, journal_id: str):
        items = self._read_all()
        self._write_all([j for j in items if j["id"] != journal_id])

    @staticmethod
    def _from_dict(d: dict) -> Journal:
        j = Journal(
            user_id=d["user_id"],
            journal_date=date.fromisoformat(d["journal_date"]),
            content=d.get("content", ""),
            weather=d.get("weather", ""),
            mood=d.get("mood", ""),
            images=d.get("images", []),
        )
        j.id = d["id"]
        j.created_at = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        j.updated_at = datetime.fromisoformat(d["updated_at"]) if d.get("updated_at") else datetime.now()
        return j


class JSONJournalCommentStorage:
    """JSON storage for journal comments."""

    def __init__(self, filepath: str = "journal_comments.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, comment: JournalComment):
        items = self._read_all()
        for i, c in enumerate(items):
            if c["id"] == comment.id:
                items[i] = comment.to_dict()
                self._write_all(items)
                return
        items.append(comment.to_dict())
        self._write_all(items)

    def get_by_journal(self, journal_id: str) -> List[JournalComment]:
        result = []
        for c in self._read_all():
            if c["journal_id"] == journal_id:
                comment = JournalComment(
                    journal_id=c["journal_id"],
                    user_id=c["user_id"],
                    content=c.get("content", ""),
                )
                comment.id = c["id"]
                comment.created_at = datetime.fromisoformat(c["created_at"]) if c.get("created_at") else datetime.now()
                result.append(comment)
        result.sort(key=lambda x: x.created_at)
        return result

    def delete(self, comment_id: str):
        items = self._read_all()
        self._write_all([c for c in items if c["id"] != comment_id])

    def get(self, comment_id: str) -> Optional[JournalComment]:
        for c in self._read_all():
            if c["id"] == comment_id:
                comment = JournalComment(
                    journal_id=c["journal_id"],
                    user_id=c["user_id"],
                    content=c.get("content", ""),
                )
                comment.id = c["id"]
                comment.created_at = datetime.fromisoformat(c["created_at"]) if c.get("created_at") else datetime.now()
                return comment
        return None

    def delete_by_journal(self, journal_id: str):
        items = self._read_all()
        self._write_all([c for c in items if c["journal_id"] != journal_id])


class JSONPomodoroStorage:
    """JSON storage for pomodoro sessions."""

    def __init__(self, filepath: str = "pomodoro_sessions.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, session: PomodoroSession):
        items = self._read_all()
        d = session.to_dict()
        for i, s in enumerate(items):
            if s["id"] == session.id:
                items[i] = d
                self._write_all(items)
                return
        items.append(d)
        self._write_all(items)

    def get(self, session_id: str) -> Optional[PomodoroSession]:
        for s in self._read_all():
            if s["id"] == session_id:
                return self._from_dict(s)
        return None

    def get_by_user(self, user_id: str, filter_date: date = None) -> List[PomodoroSession]:
        result = []
        for s in self._read_all():
            if s.get("user_id") != user_id:
                continue
            if filter_date:
                st = datetime.fromisoformat(s["start_time"]).date()
                if st != filter_date:
                    continue
            result.append(self._from_dict(s))
        result.sort(key=lambda x: x.start_time, reverse=True)
        return result

    @staticmethod
    def _from_dict(d: dict) -> PomodoroSession:
        s = PomodoroSession(
            user_id=d["user_id"],
            duration=d.get("duration", 25),
            activity_id=d.get("activity_id"),
            label=d.get("label"),
            status=d.get("status", "active"),
        )
        s.id = d["id"]
        s.start_time = datetime.fromisoformat(d["start_time"]) if d.get("start_time") else datetime.now()
        s.end_time = datetime.fromisoformat(d["end_time"]) if d.get("end_time") else None
        s.created_at = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        return s


class JSONGoalStorage:
    """JSON storage for goals."""

    def __init__(self, filepath: str = "goals.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, goal: Goal):
        items = self._read_all()
        d = goal.to_dict()
        for i, g in enumerate(items):
            if g["id"] == goal.id:
                items[i] = d
                self._write_all(items)
                return
        items.append(d)
        self._write_all(items)

    def get(self, goal_id: str) -> Optional[Goal]:
        for g in self._read_all():
            if g["id"] == goal_id:
                return self._from_dict(g)
        return None

    def get_by_user(self, user_id: str) -> List[Goal]:
        result = []
        for g in self._read_all():
            if g.get("user_id") == user_id:
                result.append(self._from_dict(g))
        result.sort(key=lambda x: x.created_at, reverse=True)
        return result

    def delete(self, goal_id: str) -> bool:
        items = self._read_all()
        filtered = [g for g in items if g["id"] != goal_id]
        if len(filtered) == len(items):
            return False
        self._write_all(filtered)
        return True

    @staticmethod
    def _from_dict(d: dict) -> Goal:
        g = Goal(
            title=d["title"],
            user_id=d["user_id"],
            description=d.get("description", ""),
            target_value=d.get("target_value", 1),
            unit=d.get("unit", ""),
            period=d.get("period", "weekly"),
            category_id=d.get("category_id"),
        )
        g.id = d["id"]
        if d.get("start_date"):
            g.start_date = date.fromisoformat(d["start_date"])
        if d.get("end_date"):
            g.end_date = date.fromisoformat(d["end_date"])
        g.created_at = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        g.updated_at = datetime.fromisoformat(d["updated_at"]) if d.get("updated_at") else datetime.now()
        return g


class JSONGoalProgressStorage:
    """JSON storage for goal progress entries."""

    def __init__(self, filepath: str = "goal_progress.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, progress: GoalProgress):
        items = self._read_all()
        d = progress.to_dict()
        for i, p in enumerate(items):
            if p["id"] == progress.id:
                items[i] = d
                self._write_all(items)
                return
        items.append(d)
        self._write_all(items)

    def get_by_goal(self, goal_id: str) -> List[GoalProgress]:
        result = []
        for p in self._read_all():
            if p["goal_id"] == goal_id:
                gp = GoalProgress(
                    goal_id=p["goal_id"],
                    value=p.get("value", 0),
                    note=p.get("note", ""),
                    progress_date=date.fromisoformat(p["progress_date"]) if p.get("progress_date") else date.today(),
                )
                gp.id = p["id"]
                gp.created_at = datetime.fromisoformat(p["created_at"]) if p.get("created_at") else datetime.now()
                result.append(gp)
        result.sort(key=lambda x: x.progress_date, reverse=True)
        return result

    def delete_by_goal(self, goal_id: str):
        items = self._read_all()
        self._write_all([p for p in items if p["goal_id"] != goal_id])


class JSONTemplateStorage:
    """JSON storage for activity templates."""

    def __init__(self, filepath: str = "templates.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, template: ActivityTemplate):
        items = self._read_all()
        d = template.to_dict()
        for i, t in enumerate(items):
            if t["id"] == template.id:
                items[i] = d
                self._write_all(items)
                return
        items.append(d)
        self._write_all(items)

    def get(self, template_id: str) -> Optional[ActivityTemplate]:
        for t in self._read_all():
            if t["id"] == template_id:
                return self._from_dict(t)
        return None

    def get_by_user(self, user_id: str) -> List[ActivityTemplate]:
        result = []
        for t in self._read_all():
            if t.get("user_id") == user_id:
                result.append(self._from_dict(t))
        result.sort(key=lambda x: x.created_at, reverse=True)
        return result

    def delete(self, template_id: str) -> bool:
        items = self._read_all()
        filtered = [t for t in items if t["id"] != template_id]
        if len(filtered) == len(items):
            return False
        self._write_all(filtered)
        return True

    @staticmethod
    def _from_dict(d: dict) -> ActivityTemplate:
        t = ActivityTemplate(
            title=d["title"],
            user_id=d["user_id"],
            description=d.get("description", ""),
            priority=d.get("priority", "medium"),
            category_id=d.get("category_id"),
            duration_minutes=d.get("duration_minutes"),
            tags=d.get("tags", []),
        )
        t.id = d["id"]
        t.created_at = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        return t


class JSONSharedActivityStorage:
    """JSON storage for shared activity records."""

    def __init__(self, filepath: str = "shared_activities.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, shared: SharedActivity):
        items = self._read_all()
        d = shared.to_dict()
        for i, s in enumerate(items):
            if s["id"] == shared.id:
                items[i] = d
                self._write_all(items)
                return
        items.append(d)
        self._write_all(items)

    def get_by_activity(self, activity_id: str) -> List[SharedActivity]:
        result = []
        for s in self._read_all():
            if s["activity_id"] == activity_id:
                result.append(self._from_dict(s))
        return result

    def get_shared_with_user(self, user_id: str) -> List[SharedActivity]:
        result = []
        for s in self._read_all():
            if s["shared_with_id"] == user_id:
                result.append(self._from_dict(s))
        return result

    def delete(self, activity_id: str, shared_with_id: str) -> bool:
        items = self._read_all()
        filtered = [s for s in items if not (s["activity_id"] == activity_id and s["shared_with_id"] == shared_with_id)]
        if len(filtered) == len(items):
            return False
        self._write_all(filtered)
        return True

    def find(self, activity_id: str, shared_with_id: str) -> Optional[SharedActivity]:
        for s in self._read_all():
            if s["activity_id"] == activity_id and s["shared_with_id"] == shared_with_id:
                return self._from_dict(s)
        return None

    @staticmethod
    def _from_dict(d: dict) -> SharedActivity:
        s = SharedActivity(
            activity_id=d["activity_id"],
            owner_id=d["owner_id"],
            shared_with_id=d["shared_with_id"],
            permission=d.get("permission", "view"),
        )
        s.id = d["id"]
        s.created_at = datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now()
        return s
