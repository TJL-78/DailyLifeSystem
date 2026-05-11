"""Data models for the Daily Activity Management System."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, List


class ActivityStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrenceType(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Category:
    """Activity category."""
    name: str
    user_id: str
    color: str = "#3498db"
    icon: str = ""
    sort_order: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "color": self.color,
            "icon": self.icon,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Activity:
    """Represents a daily activity."""
    title: str
    user_id: str
    description: str = ""
    status: ActivityStatus = ActivityStatus.PENDING
    priority: ActivityPriority = ActivityPriority.MEDIUM
    category_id: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    recurrence: RecurrenceType = RecurrenceType.NONE
    recurrence_end_date: Optional[date] = None
    parent_id: Optional[str] = None
    sort_order: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def complete(self):
        self.status = ActivityStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def cancel(self):
        self.status = ActivityStatus.CANCELLED
        self.updated_at = datetime.now()

    def start(self):
        self.status = ActivityStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "category_id": self.category_id,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "duration_minutes": self.duration_minutes,
            "tags": self.tags,
            "recurrence": self.recurrence.value,
            "recurrence_end_date": self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class Habit:
    """A habit to track."""
    name: str
    user_id: str
    description: str = ""
    frequency: str = "daily"  # daily or weekly
    target_count: int = 1
    color: str = "#27ae60"
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "frequency": self.frequency,
            "target_count": self.target_count,
            "color": self.color,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class HabitRecord:
    """A single check-in record for a habit."""
    habit_id: str
    record_date: date
    count: int = 1
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "record_date": self.record_date.isoformat(),
            "count": self.count,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Journal:
    """A daily journal entry."""
    user_id: str
    journal_date: date
    content: str = ""
    weather: str = ""
    mood: str = ""
    images: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "journal_date": self.journal_date.isoformat(),
            "content": self.content,
            "weather": self.weather,
            "mood": self.mood,
            "images": self.images,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class JournalComment:
    """A comment on a journal entry."""
    journal_id: str
    user_id: str
    content: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "journal_id": self.journal_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class PomodoroSession:
    """A pomodoro/focus timer session."""
    user_id: str
    duration: int = 25
    activity_id: Optional[str] = None
    label: Optional[str] = None
    status: str = "active"  # active, completed, cancelled
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "duration": self.duration,
            "activity_id": self.activity_id,
            "label": self.label,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Goal:
    """A goal to track progress toward."""
    title: str
    user_id: str
    description: str = ""
    target_value: int = 1
    unit: str = ""
    period: str = "weekly"  # weekly, monthly, yearly
    category_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "description": self.description,
            "target_value": self.target_value,
            "unit": self.unit,
            "period": self.period,
            "category_id": self.category_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class GoalProgress:
    """A progress entry for a goal."""
    goal_id: str
    value: int = 0
    note: str = ""
    progress_date: date = field(default_factory=date.today)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "value": self.value,
            "note": self.note,
            "progress_date": self.progress_date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ActivityTemplate:
    """A reusable activity template."""
    title: str
    user_id: str
    description: str = ""
    priority: Optional[str] = "medium"
    category_id: Optional[str] = None
    duration_minutes: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "description": self.description,
            "priority": self.priority,
            "category_id": self.category_id,
            "duration_minutes": self.duration_minutes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SharedActivity:
    """A record of sharing an activity with another user."""
    activity_id: str
    owner_id: str
    shared_with_id: str
    permission: str = "view"  # "view" or "edit"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "activity_id": self.activity_id,
            "owner_id": self.owner_id,
            "shared_with_id": self.shared_with_id,
            "permission": self.permission,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SleepRecord:
    """A daily sleep record."""
    user_id: str
    record_date: date
    sleep_time: Optional[str] = None  # HH:MM format
    wake_time: Optional[str] = None   # HH:MM format
    duration_hours: float = 0.0
    quality: int = 3  # 1-5 rating
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "user_id": self.user_id,
            "record_date": self.record_date.isoformat(),
            "sleep_time": self.sleep_time, "wake_time": self.wake_time,
            "duration_hours": self.duration_hours, "quality": self.quality,
            "note": self.note, "created_at": self.created_at.isoformat(),
        }


@dataclass
class MoodRecord:
    """A daily mood entry."""
    user_id: str
    record_date: date
    mood: str = "neutral"  # happy, calm, sad, angry, tired, excited, anxious, neutral
    energy: int = 3  # 1-5
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "user_id": self.user_id,
            "record_date": self.record_date.isoformat(),
            "mood": self.mood, "energy": self.energy,
            "note": self.note, "created_at": self.created_at.isoformat(),
        }


@dataclass
class HealthRecord:
    """Daily health data (exercise, water, etc)."""
    user_id: str
    record_date: date
    exercise_type: str = ""  # running, walking, gym, yoga, cycling, swimming, other
    exercise_minutes: int = 0
    exercise_calories: int = 0
    water_ml: int = 0
    steps: int = 0
    weight_kg: float = 0.0
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "user_id": self.user_id,
            "record_date": self.record_date.isoformat(),
            "exercise_type": self.exercise_type,
            "exercise_minutes": self.exercise_minutes,
            "exercise_calories": self.exercise_calories,
            "water_ml": self.water_ml, "steps": self.steps,
            "weight_kg": self.weight_kg, "note": self.note,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class FinanceRecord:
    """A financial transaction record."""
    user_id: str
    record_date: date
    amount: float = 0.0
    record_type: str = "expense"  # income or expense
    category: str = ""  # food, transport, shopping, entertainment, salary, other
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "user_id": self.user_id,
            "record_date": self.record_date.isoformat(),
            "amount": self.amount, "record_type": self.record_type,
            "category": self.category, "note": self.note,
            "created_at": self.created_at.isoformat(),
        }
