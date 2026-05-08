"""Flask Web API for the Daily Activity Management System."""

import os
from datetime import date, time, datetime
from functools import wraps
from flask import Flask, jsonify, request, render_template, session, redirect, url_for

from .models import Activity, ActivityStatus, ActivityPriority, RecurrenceType, Category
from .user_model import User

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "daily-life-system-secret-key-change-me")

# Storage initialization
_use_mysql = os.environ.get("USE_MYSQL", "").lower() in ("1", "true", "yes")

if _use_mysql:
    from .database import Database, MySQLUserStorage, MySQLCategoryStorage, MySQLActivityStorage
    _db = Database()
    user_storage = MySQLUserStorage(_db)
    category_storage = MySQLCategoryStorage(_db)
    activity_storage = MySQLActivityStorage(_db)
else:
    from .user_storage import JSONUserStorage
    from .json_storage import JSONActivityStorage, JSONCategoryStorage
    user_storage = JSONUserStorage("users.json")
    category_storage = JSONCategoryStorage("categories.json")
    activity_storage = JSONActivityStorage("activities.json")


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


@app.route("/api/stats", methods=["GET"])
@login_required
def get_stats():
    return jsonify(activity_storage.get_stats(current_user_id()))


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
