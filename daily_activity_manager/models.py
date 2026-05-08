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
