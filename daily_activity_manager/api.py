"""Flask Web API for the Daily Activity Management System."""

import os
import csv
import io
import re
import base64
from datetime import date, time, datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, Response, send_from_directory

from .models import Activity, ActivityStatus, ActivityPriority, RecurrenceType, Category, Habit, HabitRecord
from .user_model import User

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "daily-life-system-secret-key-change-me")

# Avatar upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'avatars')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Storage initialization
_use_mysql = os.environ.get("USE_MYSQL", "").lower() in ("1", "true", "yes")

if _use_mysql:
    from .database import Database, MySQLUserStorage, MySQLCategoryStorage, MySQLActivityStorage, MySQLHabitStorage, MySQLHabitRecordStorage
    _db = Database()
    user_storage = MySQLUserStorage(_db)
    category_storage = MySQLCategoryStorage(_db)
    activity_storage = MySQLActivityStorage(_db)
    habit_storage = MySQLHabitStorage(_db)
    habit_record_storage = MySQLHabitRecordStorage(_db)
else:
    from .user_storage import JSONUserStorage
    from .json_storage import JSONActivityStorage, JSONCategoryStorage, JSONHabitStorage, JSONHabitRecordStorage
    user_storage = JSONUserStorage("users.json")
    category_storage = JSONCategoryStorage("categories.json")
    activity_storage = JSONActivityStorage("activities.json")
    habit_storage = JSONHabitStorage("habits.json")
    habit_record_storage = JSONHabitRecordStorage("habit_records.json")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "login required"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def current_user_id():
    return session.get("user_id")


# ---- Auth Routes ----

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email = data.get("email", "").strip()
    display_name = data.get("display_name", "").strip()

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    if len(username) < 3:
        return jsonify({"error": "用户名至少3个字符"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少6个字符"}), 400
    if user_storage.username_exists(username):
        return jsonify({"error": "用户名已存在"}), 409

    user = User(
        username=username,
        password_hash=User.hash_password(password),
        email=email,
        display_name=display_name or username,
    )
    user_storage.save(user)

    # Create default categories for the new user
    defaults = [
        ("工作", "#3498db", "💼"),
        ("学习", "#9b59b6", "📚"),
        ("健身", "#27ae60", "🏃"),
        ("生活", "#f39c12", "🏠"),
        ("娱乐", "#e74c3c", "🎮"),
    ]
    for i, (name, color, icon) in enumerate(defaults):
        cat = Category(name=name, user_id=user.id, color=color, icon=icon, sort_order=i)
        category_storage.save(cat)

    session["user_id"] = user.id
    session["username"] = user.username
    return jsonify({"message": "注册成功", "user": user.to_dict()}), 201


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    user = user_storage.get_by_username(username)
    if not user or not User.verify_password(password, user.password_hash):
        return jsonify({"error": "用户名或密码错误"}), 401

    session["user_id"] = user.id
    session["username"] = user.username
    return jsonify({"message": "登录成功", "user": user.to_dict()})


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "已退出登录"})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    if "user_id" not in session:
        return jsonify({"logged_in": False}), 401
    user = user_storage.get_by_id(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"logged_in": False}), 401
    return jsonify({"logged_in": True, "user": user.to_dict()})


# ---- Category Routes ----

@app.route("/api/categories", methods=["GET"])
@login_required
def list_categories():
    categories = category_storage.get_by_user(current_user_id())
    return jsonify([c.to_dict() for c in categories])


@app.route("/api/categories", methods=["POST"])
@login_required
def create_category():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    cat = Category(
        name=data["name"],
        user_id=current_user_id(),
        color=data.get("color", "#3498db"),
        icon=data.get("icon", ""),
        sort_order=data.get("sort_order", 0),
    )
    category_storage.save(cat)
    return jsonify(cat.to_dict()), 201


@app.route("/api/categories/<cat_id>", methods=["PUT"])
@login_required
def update_category(cat_id):
    cat = category_storage.get(cat_id)
    if not cat or cat.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    if data.get("name"):
        cat.name = data["name"]
    if "color" in data:
        cat.color = data["color"]
    if "icon" in data:
        cat.icon = data["icon"]
    if "sort_order" in data:
        cat.sort_order = data["sort_order"]
    category_storage.save(cat)
    return jsonify(cat.to_dict())


@app.route("/api/categories/<cat_id>", methods=["DELETE"])
@login_required
def delete_category(cat_id):
    cat = category_storage.get(cat_id)
    if not cat or cat.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    category_storage.delete(cat_id)
    return jsonify({"message": "deleted"})


# ---- Activity Routes ----

@app.route("/api/activities", methods=["GET"])
@login_required
def list_activities():
    status = request.args.get("status")
    priority = request.args.get("priority")
    category_id = request.args.get("category_id")
    today_only = request.args.get("today", "").lower() == "true"
    scheduled_date = date.today() if today_only else None

    activities = activity_storage.get_by_user(
        current_user_id(), status=status, priority=priority,
        category_id=category_id, scheduled_date=scheduled_date
    )
    return jsonify([a.to_dict() for a in activities])


@app.route("/api/activities", methods=["POST"])
@login_required
def create_activity():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    activity = Activity(
        title=data["title"],
        user_id=current_user_id(),
        description=data.get("description", ""),
        priority=ActivityPriority(data.get("priority", "medium")),
        category_id=data.get("category_id"),
        scheduled_date=date.fromisoformat(data["scheduled_date"]) if data.get("scheduled_date") else None,
        scheduled_time=time.fromisoformat(data["scheduled_time"]) if data.get("scheduled_time") else None,
        due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        due_time=time.fromisoformat(data["due_time"]) if data.get("due_time") else None,
        duration_minutes=data.get("duration_minutes"),
        tags=data.get("tags", []),
        recurrence=RecurrenceType(data.get("recurrence", "none")),
        parent_id=data.get("parent_id"),
    )
    activity_storage.save(activity)
    return jsonify(activity.to_dict()), 201


@app.route("/api/activities/<activity_id>", methods=["GET"])
@login_required
def get_activity(activity_id):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>", methods=["PUT"])
@login_required
def update_activity(activity_id):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    if "title" in data:
        activity.title = data["title"]
    if "description" in data:
        activity.description = data["description"]
    if "priority" in data:
        activity.priority = ActivityPriority(data["priority"])
    if "category_id" in data:
        activity.category_id = data["category_id"] or None
    if "scheduled_date" in data:
        activity.scheduled_date = date.fromisoformat(data["scheduled_date"]) if data["scheduled_date"] else None
    if "scheduled_time" in data:
        activity.scheduled_time = time.fromisoformat(data["scheduled_time"]) if data["scheduled_time"] else None
    if "due_date" in data:
        activity.due_date = date.fromisoformat(data["due_date"]) if data["due_date"] else None
    if "recurrence" in data:
        activity.recurrence = RecurrenceType(data["recurrence"])
    if "tags" in data:
        activity.tags = data["tags"]

    activity.updated_at = datetime.now()
    activity_storage.save(activity)
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/complete", methods=["POST"])
@login_required
def complete_activity(activity_id):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    activity.complete()
    activity_storage.save(activity)
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/start", methods=["POST"])
@login_required
def start_activity(activity_id):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    activity.start()
    activity_storage.save(activity)
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/cancel", methods=["POST"])
@login_required
def cancel_activity(activity_id):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    activity.cancel()
    activity_storage.save(activity)
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>", methods=["DELETE"])
@login_required
def delete_activity(activity_id):
    activity = activity_storage.get(activity_id)
    if not activity or activity.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    activity_storage.delete(activity_id)
    return jsonify({"message": "deleted"})


# ---- Search ----

@app.route("/api/activities/search", methods=["GET"])
@login_required
def search_activities():
    """Search activities by keyword in title/description."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    activities = activity_storage.get_by_user(current_user_id())
    q_lower = q.lower()
    results = [a for a in activities if q_lower in a.title.lower() or q_lower in a.description.lower() or any(q_lower in t.lower() for t in a.tags)]
    return jsonify([a.to_dict() for a in results])


# ---- Subtasks ----

@app.route("/api/activities/<activity_id>/subtasks", methods=["GET"])
@login_required
def list_subtasks(activity_id):
    """List subtasks of an activity."""
    parent = activity_storage.get(activity_id)
    if not parent or parent.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    all_activities = activity_storage.get_by_user(current_user_id())
    subtasks = [a for a in all_activities if a.parent_id == activity_id]
    return jsonify([a.to_dict() for a in subtasks])


@app.route("/api/activities/<activity_id>/subtasks", methods=["POST"])
@login_required
def create_subtask(activity_id):
    """Create a subtask under a parent activity."""
    parent = activity_storage.get(activity_id)
    if not parent or parent.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    subtask = Activity(
        title=data["title"],
        user_id=current_user_id(),
        description=data.get("description", ""),
        priority=ActivityPriority(data.get("priority", parent.priority.value)),
        category_id=parent.category_id,
        scheduled_date=parent.scheduled_date,
        parent_id=activity_id,
        tags=data.get("tags", []),
    )
    activity_storage.save(subtask)
    return jsonify(subtask.to_dict()), 201


# ---- Calendar data ----

@app.route("/api/activities/calendar", methods=["GET"])
@login_required
def calendar_activities():
    """Get activities for a date range (for calendar view)."""
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end:
        return jsonify({"error": "start and end required"}), 400
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    all_activities = activity_storage.get_by_user(current_user_id())
    results = []
    for a in all_activities:
        d = a.scheduled_date or a.due_date
        if d and start_date <= d <= end_date:
            results.append(a)
    return jsonify([a.to_dict() for a in results])


@app.route("/api/stats", methods=["GET"])
@login_required
def get_stats():
    return jsonify(activity_storage.get_stats(current_user_id()))


# ---- Detailed Stats ----

@app.route("/api/stats/detailed", methods=["GET"])
@login_required
def get_detailed_stats():
    """Get detailed statistics for charts."""
    uid = current_user_id()
    all_acts = activity_storage.get_by_user(uid)
    cats = category_storage.get_by_user(uid)
    cat_map = {c.id: c.to_dict() for c in cats}

    # By category
    by_category = {}
    for a in all_acts:
        cname = cat_map.get(a.category_id, {}).get("name", "未分类") if a.category_id else "未分类"
        by_category[cname] = by_category.get(cname, 0) + 1

    # Weekly completion trend (last 4 weeks)
    today = date.today()
    weekly = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7 * i)
        week_end = week_start + timedelta(days=6)
        created = len([a for a in all_acts if a.created_at.date() >= week_start and a.created_at.date() <= week_end])
        completed = len([a for a in all_acts if a.completed_at and a.completed_at.date() >= week_start and a.completed_at.date() <= week_end])
        weekly.append({"week": week_start.isoformat(), "created": created, "completed": completed})

    # Total time
    total_minutes = sum(a.duration_minutes or 0 for a in all_acts if a.status == ActivityStatus.COMPLETED)

    return jsonify({
        "by_category": by_category,
        "weekly_trend": weekly,
        "total_completed_minutes": total_minutes,
        "total": len(all_acts),
        "completed": len([a for a in all_acts if a.status == ActivityStatus.COMPLETED]),
        "pending": len([a for a in all_acts if a.status == ActivityStatus.PENDING]),
    })


# ---- Habit Routes ----

@app.route("/api/habits", methods=["GET"])
@login_required
def list_habits():
    habits = habit_storage.get_by_user(current_user_id())
    return jsonify([h.to_dict() for h in habits])


@app.route("/api/habits", methods=["POST"])
@login_required
def create_habit():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name required"}), 400
    habit = Habit(
        name=data["name"],
        user_id=current_user_id(),
        description=data.get("description", ""),
        frequency=data.get("frequency", "daily"),
        target_count=data.get("target_count", 1),
        color=data.get("color", "#27ae60"),
    )
    habit_storage.save(habit)
    return jsonify(habit.to_dict()), 201


@app.route("/api/habits/<habit_id>", methods=["PUT"])
@login_required
def update_habit(habit_id):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    if "name" in data: habit.name = data["name"]
    if "description" in data: habit.description = data["description"]
    if "frequency" in data: habit.frequency = data["frequency"]
    if "target_count" in data: habit.target_count = data["target_count"]
    if "color" in data: habit.color = data["color"]
    if "is_active" in data: habit.is_active = data["is_active"]
    habit_storage.save(habit)
    return jsonify(habit.to_dict())


@app.route("/api/habits/<habit_id>", methods=["DELETE"])
@login_required
def delete_habit(habit_id):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    habit_record_storage.delete_by_habit(habit_id)
    habit_storage.delete(habit_id)
    return jsonify({"message": "deleted"})


@app.route("/api/habits/<habit_id>/checkin", methods=["POST"])
@login_required
def checkin_habit(habit_id):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    data = request.get_json() or {}
    record_date = date.fromisoformat(data["date"]) if data.get("date") else date.today()
    record = HabitRecord(habit_id=habit_id, record_date=record_date, count=data.get("count", 1), note=data.get("note", ""))
    habit_record_storage.save(record)
    return jsonify(record.to_dict()), 201


@app.route("/api/habits/<habit_id>/uncheckin", methods=["POST"])
@login_required
def uncheckin_habit(habit_id):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    data = request.get_json() or {}
    record_date = date.fromisoformat(data["date"]) if data.get("date") else date.today()
    habit_record_storage.delete_record(habit_id, record_date)
    return jsonify({"message": "unchecked"})


@app.route("/api/habits/<habit_id>/records", methods=["GET"])
@login_required
def habit_records(habit_id):
    habit = habit_storage.get(habit_id)
    if not habit or habit.user_id != current_user_id():
        return jsonify({"error": "not found"}), 404
    start = request.args.get("start")
    end = request.args.get("end")
    start_date = date.fromisoformat(start) if start else None
    end_date = date.fromisoformat(end) if end else None
    records = habit_record_storage.get_by_habit(habit_id, start_date, end_date)
    return jsonify([r.to_dict() for r in records])


# ---- Export ----

@app.route("/api/export/json", methods=["GET"])
@login_required
def export_json():
    uid = current_user_id()
    activities = [a.to_dict() for a in activity_storage.get_by_user(uid)]
    cats = [c.to_dict() for c in category_storage.get_by_user(uid)]
    habits = [h.to_dict() for h in habit_storage.get_by_user(uid)]
    import json
    data = json.dumps({"activities": activities, "categories": cats, "habits": habits}, ensure_ascii=False, indent=2)
    return Response(data, mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=daily_life_export.json'})


@app.route("/api/export/csv", methods=["GET"])
@login_required
def export_csv():
    uid = current_user_id()
    activities = activity_storage.get_by_user(uid)
    cats = {c.id: c.name for c in category_storage.get_by_user(uid)}
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
    return Response(output.getvalue(), mimetype='text/csv; charset=utf-8-sig',
                    headers={'Content-Disposition': 'attachment; filename=activities.csv'})


# ---- User Settings ----

@app.route("/api/auth/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    user = user_storage.get_by_id(current_user_id())
    if not user:
        return jsonify({"error": "not found"}), 404
    if "display_name" in data:
        user.display_name = data["display_name"]
    if "email" in data:
        user.email = data["email"]
    if "phone" in data:
        phone = data["phone"].strip()
        if phone and not re.match(r'^\+?[\d\s\-]{6,20}$', phone):
            return jsonify({"error": "手机号格式不正确"}), 400
        user.phone = phone
    user_storage.save(user)
    return jsonify({"message": "更新成功", "user": user.to_dict()})


@app.route("/api/auth/avatar", methods=["POST"])
@login_required
def upload_avatar():
    """Upload avatar image (accepts multipart file or base64 JSON)."""
    user = user_storage.get_by_id(current_user_id())
    if not user:
        return jsonify({"error": "not found"}), 404

    filename = f"{user.id}.png"
    filepath = os.path.join(UPLOAD_DIR, filename)

    if request.content_type and 'multipart' in request.content_type:
        file = request.files.get('avatar')
        if not file:
            return jsonify({"error": "请选择头像文件"}), 400
        if file.content_length and file.content_length > 2 * 1024 * 1024:
            return jsonify({"error": "头像文件不能超过2MB"}), 400
        file.save(filepath)
    else:
        data = request.get_json()
        if not data or not data.get("avatar_base64"):
            return jsonify({"error": "请提供头像数据"}), 400
        img_data = data["avatar_base64"]
        if ',' in img_data:
            img_data = img_data.split(',', 1)[1]
        try:
            raw = base64.b64decode(img_data)
        except Exception:
            return jsonify({"error": "头像数据格式错误"}), 400
        if len(raw) > 2 * 1024 * 1024:
            return jsonify({"error": "头像文件不能超过2MB"}), 400
        with open(filepath, 'wb') as f:
            f.write(raw)

    user.avatar_url = f"/uploads/avatars/{filename}"
    user_storage.save(user)
    return jsonify({"message": "头像更新成功", "avatar_url": user.avatar_url})


@app.route("/uploads/avatars/<filename>")
def serve_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/api/auth/password", methods=["PUT"])
@login_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400
    old_pw = data.get("old_password", "")
    new_pw = data.get("new_password", "")
    if not old_pw or not new_pw:
        return jsonify({"error": "请填写旧密码和新密码"}), 400
    if len(new_pw) < 6:
        return jsonify({"error": "新密码至少6个字符"}), 400
    user = user_storage.get_by_id(current_user_id())
    if not User.verify_password(old_pw, user.password_hash):
        return jsonify({"error": "旧密码错误"}), 401
    user.password_hash = User.hash_password(new_pw)
    user_storage.save(user)
    return jsonify({"message": "密码修改成功"})


# ---- Page Routes ----

@app.route("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register")
def register_page():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


def run_server(host="0.0.0.0", port=5000, debug=False):
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
