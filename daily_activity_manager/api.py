"""Flask Web API for the Daily Activity Management System."""

from datetime import date, time
from flask import Flask, jsonify, request
from .manager import ActivityManager

app = Flask(__name__)
manager = ActivityManager("activities.json")


@app.route("/api/activities", methods=["GET"])
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
def get_activity(activity_id):
    """Get a single activity."""
    activity = manager.get_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>", methods=["PUT"])
def update_activity(activity_id):
    """Update an activity."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400
    activity = manager.update_activity(activity_id, **data)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/complete", methods=["POST"])
def complete_activity(activity_id):
    """Mark activity as completed."""
    activity = manager.complete_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/start", methods=["POST"])
def start_activity(activity_id):
    """Mark activity as in progress."""
    activity = manager.start_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>/cancel", methods=["POST"])
def cancel_activity(activity_id):
    """Cancel an activity."""
    activity = manager.cancel_activity(activity_id)
    if not activity:
        return jsonify({"error": "not found"}), 404
    return jsonify(activity.to_dict())


@app.route("/api/activities/<activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    """Delete an activity."""
    if manager.delete_activity(activity_id):
        return jsonify({"message": "deleted"})
    return jsonify({"error": "not found"}), 404


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get activity statistics."""
    return jsonify(manager.get_statistics())


@app.route("/", methods=["GET"])
def index():
    """Health check."""
    return jsonify({"service": "Daily Activity Management System", "version": "0.1.0", "status": "running"})


def run_server(host="0.0.0.0", port=5000, debug=False):
    """Run the Flask server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
