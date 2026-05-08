"""MySQL storage backend for activities."""

import os
from typing import List, Optional
from datetime import datetime, date, time

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

from .models import Activity, ActivityStatus, ActivityPriority, RecurrenceType


class MySQLStorage:
    """MySQL-based storage for activities."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ):
        self.host = host or os.environ.get("MYSQL_HOST", "localhost")
        self.port = port or int(os.environ.get("MYSQL_PORT", "3306"))
        self.user = user or os.environ.get("MYSQL_USER", "root")
        self.password = password or os.environ.get("MYSQL_PASSWORD", "")
        self.database = database or os.environ.get("MYSQL_DATABASE", "daily_life_system")
        self._init_db()

    def _get_connection(self):
        """Get a database connection."""
        import pymysql
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _init_db(self):
        """Initialize the database and create tables if needed."""
        import pymysql
        # First connect without database to create it if needed
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset="utf8mb4",
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            conn.commit()
        finally:
            conn.close()

        # Now create tables
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activities (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        scheduled_date DATE,
                        scheduled_time TIME,
                        duration_minutes INT,
                        category VARCHAR(100),
                        tags TEXT,
                        recurrence VARCHAR(20) NOT NULL DEFAULT 'none',
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        completed_at DATETIME
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            conn.commit()
        finally:
            conn.close()

    def save(self, activity: Activity):
        """Save or update an activity."""
        import json
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO activities
                        (id, title, description, status, priority, scheduled_date,
                         scheduled_time, duration_minutes, category, tags, recurrence,
                         created_at, updated_at, completed_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        title=VALUES(title), description=VALUES(description),
                        status=VALUES(status), priority=VALUES(priority),
                        scheduled_date=VALUES(scheduled_date),
                        scheduled_time=VALUES(scheduled_time),
                        duration_minutes=VALUES(duration_minutes),
                        category=VALUES(category), tags=VALUES(tags),
                        recurrence=VALUES(recurrence),
                        updated_at=VALUES(updated_at),
                        completed_at=VALUES(completed_at)
                    """,
                    (
                        activity.id,
                        activity.title,
                        activity.description,
                        activity.status.value,
                        activity.priority.value,
                        activity.scheduled_date,
                        activity.scheduled_time,
                        activity.duration_minutes,
                        activity.category,
                        json.dumps(activity.tags, ensure_ascii=False),
                        activity.recurrence.value,
                        activity.created_at,
                        activity.updated_at,
                        activity.completed_at,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _row_to_activity(self, row: dict) -> Activity:
        """Convert a database row to an Activity object."""
        import json
        tags = json.loads(row["tags"]) if row["tags"] else []
        activity = Activity(
            title=row["title"],
            description=row["description"] or "",
            status=ActivityStatus(row["status"]),
            priority=ActivityPriority(row["priority"]),
            scheduled_date=row["scheduled_date"],
            scheduled_time=row["scheduled_time"] if isinstance(row["scheduled_time"], time) else None,
            duration_minutes=row["duration_minutes"],
            category=row["category"] or "",
            tags=tags,
            recurrence=RecurrenceType(row["recurrence"]),
        )
        activity.id = row["id"]
        activity.created_at = row["created_at"]
        activity.updated_at = row["updated_at"]
        activity.completed_at = row["completed_at"]
        # Handle timedelta from MySQL TIME field
        if row["scheduled_time"] and not isinstance(row["scheduled_time"], time):
            total_seconds = int(row["scheduled_time"].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            activity.scheduled_time = time(hours, minutes, seconds)
        return activity

    def get(self, activity_id: str) -> Optional[Activity]:
        """Get an activity by ID."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_activity(row)
                return None
        finally:
            conn.close()

    def get_all(self) -> List[Activity]:
        """Get all activities."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM activities ORDER BY created_at DESC")
                return [self._row_to_activity(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, activity_id: str) -> bool:
        """Delete an activity by ID."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM activities WHERE id = %s", (activity_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
