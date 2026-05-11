"""Entry point to run the web server."""

if __name__ == "__main__":
    from daily_activity_manager.api import run_server
    run_server(host="0.0.0.0", port=5000, debug=True)
