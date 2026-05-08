"""MySQL storage backend with full schema support."""

import os
import json
from typing import List, Optional
from datetime import datetime, date, time

import pymysql
import pymysql.cursors

from .models import Activity, ActivityStatus, ActivityPriority, RecurrenceType, Category, Habit, HabitRecord
from .user_model import User


class Database:
    """Central database connection and schema manager."""

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

    def get_connection(self):
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
        conn = pymysql.connect(
            host=self.host, port=self.port, user=self.user,
            password=self.password, charset="utf8mb4",
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

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(100) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(255),
                        display_name VARCHAR(255),
                        avatar_url VARCHAR(500),
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        color VARCHAR(7) DEFAULT '#3498db',
                        icon VARCHAR(50) DEFAULT '',
                        sort_order INT DEFAULT 0,
                        created_at DATETIME NOT NULL,
                        INDEX idx_user (user_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activities (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                        category_id VARCHAR(36),
                        scheduled_date DATE,
                        scheduled_time TIME,
                        due_date DATE,
                        due_time TIME,
                        duration_minutes INT,
                        tags TEXT,
                        recurrence VARCHAR(20) NOT NULL DEFAULT 'none',
                        recurrence_end_date DATE,
                        parent_id VARCHAR(36),
                        sort_order INT DEFAULT 0,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        completed_at DATETIME,
                        INDEX idx_user (user_id),
                        INDEX idx_user_status (user_id, status),
                        INDEX idx_user_date (user_id, scheduled_date)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habits (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        frequency VARCHAR(20) DEFAULT 'daily',
                        target_count INT DEFAULT 1,
                        color VARCHAR(7) DEFAULT '#27ae60',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at DATETIME NOT NULL,
                        INDEX idx_user (user_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habit_records (
                        id VARCHAR(36) PRIMARY KEY,
                        habit_id VARCHAR(36) NOT NULL,
                        record_date DATE NOT NULL,
                        count INT DEFAULT 1,
                        note TEXT,
                        created_at DATETIME NOT NULL,
                        UNIQUE KEY uq_habit_date (habit_id, record_date),
                        INDEX idx_habit (habit_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
            conn.commit()
        finally:
            conn.close()


class MySQLUserStorage:
    """MySQL user storage."""

    def __init__(self, db: Database):
        self.db = db

    def save(self, user: User):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (id, username, password_hash, email, display_name, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        password_hash=VALUES(password_hash), email=VALUES(email),
                        display_name=VALUES(display_name), updated_at=NOW()
                """, (user.id, user.username, user.password_hash, user.email, user.display_name, user.created_at))
            conn.commit()
        finally:
            conn.close()

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()
                return User.from_dict(row) if row else None
        finally:
            conn.close()

    def get_by_id(self, user_id: str) -> Optional[User]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                return User.from_dict(row) if row else None
        finally:
            conn.close()

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None


class MySQLCategoryStorage:
    """MySQL category storage."""

    def __init__(self, db: Database):
        self.db = db

    def save(self, category: Category):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO categories (id, user_id, name, color, icon, sort_order, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name), color=VALUES(color), icon=VALUES(icon), sort_order=VALUES(sort_order)
                """, (category.id, category.user_id, category.name, category.color, category.icon, category.sort_order, category.created_at))
            conn.commit()
        finally:
            conn.close()

    def get_by_user(self, user_id: str) -> List[Category]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM categories WHERE user_id = %s ORDER BY sort_order, name", (user_id,))
                rows = cursor.fetchall()
                return [self._row_to_category(r) for r in rows]
        finally:
            conn.close()

    def get(self, category_id: str) -> Optional[Category]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
                row = cursor.fetchone()
                return self._row_to_category(row) if row else None
        finally:
            conn.close()

    def delete(self, category_id: str) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                # Clear category_id from activities first
                cursor.execute("UPDATE activities SET category_id = NULL WHERE category_id = %s", (category_id,))
                cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def _row_to_category(self, row: dict) -> Category:
        c = Category(name=row["name"], user_id=row["user_id"], color=row.get("color", "#3498db"), icon=row.get("icon", ""))
        c.id = row["id"]
        c.sort_order = row.get("sort_order", 0)
        c.created_at = row["created_at"]
        return c


class MySQLActivityStorage:
    """MySQL activity storage."""

    def __init__(self, db: Database):
        self.db = db

    def save(self, activity: Activity):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO activities
                        (id, user_id, title, description, status, priority, category_id,
                         scheduled_date, scheduled_time, due_date, due_time, duration_minutes,
                         tags, recurrence, recurrence_end_date, parent_id, sort_order,
                         created_at, updated_at, completed_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        title=VALUES(title), description=VALUES(description),
                        status=VALUES(status), priority=VALUES(priority),
                        category_id=VALUES(category_id),
                        scheduled_date=VALUES(scheduled_date), scheduled_time=VALUES(scheduled_time),
                        due_date=VALUES(due_date), due_time=VALUES(due_time),
                        duration_minutes=VALUES(duration_minutes), tags=VALUES(tags),
                        recurrence=VALUES(recurrence), recurrence_end_date=VALUES(recurrence_end_date),
                        parent_id=VALUES(parent_id), sort_order=VALUES(sort_order),
                        updated_at=VALUES(updated_at), completed_at=VALUES(completed_at)
                """, (
                    activity.id, activity.user_id, activity.title, activity.description,
                    activity.status.value, activity.priority.value, activity.category_id,
                    activity.scheduled_date, activity.scheduled_time,
                    activity.due_date, activity.due_time,
                    activity.duration_minutes,
                    json.dumps(activity.tags, ensure_ascii=False),
                    activity.recurrence.value, activity.recurrence_end_date,
                    activity.parent_id, activity.sort_order,
                    activity.created_at, activity.updated_at, activity.completed_at,
                ))
            conn.commit()
        finally:
            conn.close()

    def get(self, activity_id: str) -> Optional[Activity]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM activities WHERE id = %s", (activity_id,))
                row = cursor.fetchone()
                return self._row_to_activity(row) if row else None
        finally:
            conn.close()

    def get_by_user(self, user_id: str, status: str = None, priority: str = None,
                    category_id: str = None, scheduled_date: date = None) -> List[Activity]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM activities WHERE user_id = %s"
                params = [user_id]
                if status:
                    sql += " AND status = %s"
                    params.append(status)
                if priority:
                    sql += " AND priority = %s"
                    params.append(priority)
                if category_id:
                    sql += " AND category_id = %s"
                    params.append(category_id)
                if scheduled_date:
                    sql += " AND scheduled_date = %s"
                    params.append(scheduled_date)
                sql += " ORDER BY sort_order, created_at DESC"
                cursor.execute(sql, params)
                return [self._row_to_activity(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, activity_id: str) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM activities WHERE id = %s", (activity_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_stats(self, user_id: str) -> dict:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT status, COUNT(*) as cnt FROM activities WHERE user_id = %s GROUP BY status", (user_id,))
                by_status = {row["status"]: row["cnt"] for row in cursor.fetchall()}
                cursor.execute("SELECT priority, COUNT(*) as cnt FROM activities WHERE user_id = %s GROUP BY priority", (user_id,))
                by_priority = {row["priority"]: row["cnt"] for row in cursor.fetchall()}
                total = sum(by_status.values())
                return {"total": total, "by_status": by_status, "by_priority": by_priority}
        finally:
            conn.close()

    def _row_to_activity(self, row: dict) -> Activity:
        tags = json.loads(row["tags"]) if row.get("tags") else []
        scheduled_time = row.get("scheduled_time")
        if scheduled_time and not isinstance(scheduled_time, time):
            total_seconds = int(scheduled_time.total_seconds())
            h, rem = divmod(total_seconds, 3600)
            m, s = divmod(rem, 60)
            scheduled_time = time(h, m, s)
        due_time = row.get("due_time")
        if due_time and not isinstance(due_time, time):
            total_seconds = int(due_time.total_seconds())
            h, rem = divmod(total_seconds, 3600)
            m, s = divmod(rem, 60)
            due_time = time(h, m, s)

        a = Activity(
            title=row["title"],
            user_id=row["user_id"],
            description=row.get("description") or "",
            status=ActivityStatus(row["status"]),
            priority=ActivityPriority(row["priority"]),
            category_id=row.get("category_id"),
            scheduled_date=row.get("scheduled_date"),
            scheduled_time=scheduled_time,
            due_date=row.get("due_date"),
            due_time=due_time,
            duration_minutes=row.get("duration_minutes"),
            tags=tags,
            recurrence=RecurrenceType(row.get("recurrence", "none")),
            recurrence_end_date=row.get("recurrence_end_date"),
            parent_id=row.get("parent_id"),
            sort_order=row.get("sort_order", 0),
        )
        a.id = row["id"]
        a.created_at = row["created_at"]
        a.updated_at = row["updated_at"]
        a.completed_at = row.get("completed_at")
        return a


class MySQLHabitStorage:
    """MySQL habit storage."""

    def __init__(self, db: Database):
        self.db = db

    def save(self, habit: Habit):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO habits (id, user_id, name, description, frequency, target_count, color, is_active, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name), description=VALUES(description), frequency=VALUES(frequency),
                        target_count=VALUES(target_count), color=VALUES(color), is_active=VALUES(is_active)
                """, (habit.id, habit.user_id, habit.name, habit.description, habit.frequency,
                      habit.target_count, habit.color, habit.is_active, habit.created_at))
            conn.commit()
        finally:
            conn.close()

    def get_by_user(self, user_id: str) -> List[Habit]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM habits WHERE user_id = %s ORDER BY created_at", (user_id,))
                return [self._row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get(self, habit_id: str) -> Optional[Habit]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM habits WHERE id = %s", (habit_id,))
                row = cursor.fetchone()
                return self._row(row) if row else None
        finally:
            conn.close()

    def delete(self, habit_id: str) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM habit_records WHERE habit_id = %s", (habit_id,))
                cursor.execute("DELETE FROM habits WHERE id = %s", (habit_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def _row(self, r):
        h = Habit(name=r["name"], user_id=r["user_id"], description=r.get("description") or "",
                  frequency=r.get("frequency", "daily"), target_count=r.get("target_count", 1),
                  color=r.get("color", "#27ae60"), is_active=bool(r.get("is_active", True)))
        h.id = r["id"]
        h.created_at = r["created_at"]
        return h


class MySQLHabitRecordStorage:
    """MySQL habit record storage."""

    def __init__(self, db: Database):
        self.db = db

    def save(self, record: HabitRecord):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO habit_records (id, habit_id, record_date, count, note, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE count=VALUES(count), note=VALUES(note)
                """, (record.id, record.habit_id, record.record_date, record.count, record.note, record.created_at))
            conn.commit()
        finally:
            conn.close()

    def get_by_habit(self, habit_id: str, start_date: date = None, end_date: date = None) -> List[HabitRecord]:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM habit_records WHERE habit_id = %s"
                params = [habit_id]
                if start_date:
                    sql += " AND record_date >= %s"
                    params.append(start_date)
                if end_date:
                    sql += " AND record_date <= %s"
                    params.append(end_date)
                sql += " ORDER BY record_date"
                cursor.execute(sql, params)
                return [self._row(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    def delete_by_habit(self, habit_id: str):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM habit_records WHERE habit_id = %s", (habit_id,))
            conn.commit()
        finally:
            conn.close()

    def delete_record(self, habit_id: str, record_date: date) -> bool:
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM habit_records WHERE habit_id = %s AND record_date = %s", (habit_id, record_date))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def _row(self, r):
        rec = HabitRecord(habit_id=r["habit_id"], record_date=r["record_date"], count=r.get("count", 1), note=r.get("note") or "")
        rec.id = r["id"]
        rec.created_at = r["created_at"]
        return rec
