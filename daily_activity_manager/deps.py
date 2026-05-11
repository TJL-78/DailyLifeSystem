"""Shared dependencies for FastAPI routers."""

import os
import logging
from datetime import datetime, timedelta

from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

# Upload directories
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'avatars')
os.makedirs(UPLOAD_DIR, exist_ok=True)

JOURNAL_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'journals')
os.makedirs(JOURNAL_IMG_DIR, exist_ok=True)

# Login attempt tracking
_login_attempts = {}
_sms_codes = {}
LOGIN_MAX_ATTEMPTS = 3
LOGIN_LOCKOUT_SECONDS = 60

# Storage initialization
_use_mysql = os.environ.get("USE_MYSQL", "").lower() in ("1", "true", "yes")

if _use_mysql:
    from .database import Database, MySQLUserStorage, MySQLCategoryStorage, MySQLActivityStorage, MySQLHabitStorage, MySQLHabitRecordStorage, MySQLJournalStorage, MySQLJournalCommentStorage
    _db = Database()
    user_storage = MySQLUserStorage(_db)
    category_storage = MySQLCategoryStorage(_db)
    activity_storage = MySQLActivityStorage(_db)
    habit_storage = MySQLHabitStorage(_db)
    habit_record_storage = MySQLHabitRecordStorage(_db)
    journal_storage = MySQLJournalStorage(_db)
    journal_comment_storage = MySQLJournalCommentStorage(_db)
    # New features fall back to JSON storage when MySQL classes are not available
    from .json_storage import JSONPomodoroStorage, JSONGoalStorage, JSONGoalProgressStorage, JSONTemplateStorage, JSONSharedActivityStorage
    pomodoro_storage = JSONPomodoroStorage("pomodoro_sessions.json")
    goal_storage = JSONGoalStorage("goals.json")
    goal_progress_storage = JSONGoalProgressStorage("goal_progress.json")
    template_storage = JSONTemplateStorage("templates.json")
    shared_activity_storage = JSONSharedActivityStorage("shared_activities.json")
else:
    from .user_storage import JSONUserStorage
    from .json_storage import JSONActivityStorage, JSONCategoryStorage, JSONHabitStorage, JSONHabitRecordStorage, JSONJournalStorage, JSONJournalCommentStorage, JSONPomodoroStorage, JSONGoalStorage, JSONGoalProgressStorage, JSONTemplateStorage, JSONSharedActivityStorage
    user_storage = JSONUserStorage("users.json")
    category_storage = JSONCategoryStorage("categories.json")
    activity_storage = JSONActivityStorage("activities.json")
    habit_storage = JSONHabitStorage("habits.json")
    habit_record_storage = JSONHabitRecordStorage("habit_records.json")
    journal_storage = JSONJournalStorage("journals.json")
    journal_comment_storage = JSONJournalCommentStorage("journal_comments.json")
    pomodoro_storage = JSONPomodoroStorage("pomodoro_sessions.json")
    goal_storage = JSONGoalStorage("goals.json")
    goal_progress_storage = JSONGoalProgressStorage("goal_progress.json")
    template_storage = JSONTemplateStorage("templates.json")
    shared_activity_storage = JSONSharedActivityStorage("shared_activities.json")


def get_current_user_id(request: Request) -> str:
    """Dependency that checks session for authenticated user."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="login required")
    return user_id


def _get_client_key(request: Request) -> str:
    """Get a key to track login attempts per client."""
    return request.client.host if request.client else "unknown"


def _check_lockout(request: Request):
    """Check if client is locked out. Returns (locked, remaining_seconds)."""
    key = _get_client_key(request)
    info = _login_attempts.get(key)
    if info and info.get("locked_until"):
        remaining = (info["locked_until"] - datetime.now()).total_seconds()
        if remaining > 0:
            return True, int(remaining)
        else:
            _login_attempts.pop(key, None)
    return False, 0


def _record_failed_attempt(request: Request):
    """Record a failed login attempt. Returns (locked, remaining_seconds)."""
    key = _get_client_key(request)
    info = _login_attempts.get(key, {"count": 0})
    info["count"] = info.get("count", 0) + 1
    if info["count"] >= LOGIN_MAX_ATTEMPTS:
        info["locked_until"] = datetime.now() + timedelta(seconds=LOGIN_LOCKOUT_SECONDS)
        _login_attempts[key] = info
        return True, LOGIN_LOCKOUT_SECONDS
    _login_attempts[key] = info
    return False, 0


def _clear_attempts(request: Request):
    """Clear login attempts for current client."""
    key = _get_client_key(request)
    _login_attempts.pop(key, None)
