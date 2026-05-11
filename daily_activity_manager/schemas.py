"""Pydantic models for request validation."""

from typing import Optional, List
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""
    display_name: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class SmsSendRequest(BaseModel):
    phone: str


class SmsLoginRequest(BaseModel):
    phone: str
    code: str


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class AvatarBase64Request(BaseModel):
    avatar_base64: str


class CategoryCreateRequest(BaseModel):
    name: str
    color: Optional[str] = "#3498db"
    icon: Optional[str] = ""
    sort_order: Optional[int] = 0


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class ActivityCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[str] = "medium"
    category_id: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    tags: Optional[List[str]] = []
    recurrence: Optional[str] = "none"
    parent_id: Optional[str] = None


class ActivityUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[str] = None
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    due_date: Optional[str] = None
    recurrence: Optional[str] = None
    tags: Optional[List[str]] = None


class HabitCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    frequency: Optional[str] = "daily"
    target_count: Optional[int] = 1
    color: Optional[str] = "#27ae60"


class HabitUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    target_count: Optional[int] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class HabitCheckinRequest(BaseModel):
    date: Optional[str] = None
    count: Optional[int] = 1
    note: Optional[str] = ""


class JournalCreateRequest(BaseModel):
    journal_date: str
    content: Optional[str] = ""
    weather: Optional[str] = ""
    mood: Optional[str] = ""
    images: Optional[List[str]] = []


class JournalUpdateRequest(BaseModel):
    content: Optional[str] = None
    weather: Optional[str] = None
    mood: Optional[str] = None
    images: Optional[List[str]] = None


class JournalCommentCreateRequest(BaseModel):
    content: str
