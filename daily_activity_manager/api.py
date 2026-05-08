"""Flask Web API for the Daily Activity Management System."""

import os
from datetime import date, time
from functools import wraps
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from .manager import ActivityManager
from .user_model import User
from .user_storage import JSONUserStorage, MySQLUserStorage

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "daily-life-system-secret-key-change-me")
manager = ActivityManager("activities.json")

# Initialize user storage
_use_mysql = os.environ.get("USE_MYSQL", "").lower() in ("1", "true", "yes")
if _use_mysql:
    from .mysql_storage import MySQLStorage
    _ms = MySQLStorage()
    user_storage = MySQLUserStorage(_ms._get_connection)
else:
    user_storage = JSONUserStorage("users.json")


def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "login required"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


# ---- Auth Routes ----

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400

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
    session["user_id"] = user.id
    session["username"] = user.username
    return jsonify({"message": "注册成功", "user": user.to_dict()}), 201


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    """Login."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400

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
    """Logout."""
    session.clear()
    return jsonify({"message": "已退出登录"})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    """Get current user info."""
    if "user_id" not in session:
        return jsonify({"logged_in": False}), 401
    user = user_storage.get_by_id(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"logged_in": False}), 401
    return jsonify({"logged_in": True, "user": user.to_dict()})


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
    """Serve the frontend page."""
    return render_template("index.html")


# ---- Activity API (login required) ----

@app.route("/api/activities", methods=["GET"])
@login_required
def list_activities():
    """List activities with optional filters."""
    status = request.args.get("status")
    priority = request.args.get("priority")
    category = request.args.get("category")
    today_only = request.args.get("today", "").lower() == "true"

    if today_only:
        activities = manager.today_activities()
    else:
        activities = manager.list_activities(
            status=status, priority=priority, category=category
        )
    return jsonify([a.to_dict() for a in activities])


@app.route("/api/activities", methods=["POST"])
@login_required
def create_activity():
    """Create a new activity."""
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    scheduled_date = None
    if data.get("scheduled_date"):
        scheduled_date = date.fromisoformat(data["scheduled_date"])

    scheduled_time = None
    if data.get("scheduled_time"):
        scheduled_time = time.fromisoformat(data["scheduled_time"])

    activity = manager.create_activity(
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        duration_minutes=data.get("duration_minutes"),
        category=data.get("category", ""),
        tags=data.get("tags", []),
        recurrence=data.get("recurrence", "none"),
    )
    return jsonify(activity.to_dict()), 201


@app.route("/api/activities/<activity_id>", methods=["GET"])
@login_required
def get_activity(activity_id):
    activity = manager.get_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>", methods=["PUT"])
@login_required
def update_activity(activity_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400
    activity = manager.update_activity(activity_id, **data)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/complete", methods=["POST"])
@login_required
def complete_activity(activity_id):
    activity = manager.complete_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/start", methods=["POST"])
@login_required
def start_activity(activity_id):
    activity = manager.start_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/cancel", methods=["POST"])
@login_required
def cancel_activity(activity_id):
    activity = manager.cancel_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>", methods=["DELETE"])
@login_required
def delete_activity(activity_id):
    if manager.delete_activity(activity_id):
        return jsonify({"message": "deleted"})
    return jsonify({"error": "not found"}), 404


@app.route("/api/stats", methods=["GET"])
@login_required
def get_stats():
    return jsonify(manager.get_statistics())


def run_server(host="0.0.0.0", port=5000, debug=False):
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
