from flask import Flask, render_template, request, jsonify
import subprocess
import platform
import os

app = Flask(__name__)

def is_windows():
    return platform.system() == "Windows"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/action", methods=["POST"])
def perform_action():
    data = request.get_json()
    action = data.get("action", "")

    if not is_windows():
        return jsonify({
            "status": "error",
            "message": f"This tool only works on Windows (current OS: {platform.system()})"
        })

    commands = {
        "shutdown":  ["shutdown", "/s", "/t", "5"],
        "restart":   ["shutdown", "/r", "/t", "5"],
        "sleep":     ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        "hibernate": ["shutdown", "/h"],
        "lock":      ["rundll32.exe", "user32.dll,LockWorkStation"],
        "logoff":    ["shutdown", "/l"],
    }

    messages = {
        "shutdown":  "System will shut down in 5 seconds.",
        "restart":   "System will restart in 5 seconds.",
        "sleep":     "System is going to sleep.",
        "hibernate": "System is hibernating.",
        "lock":      "Screen locked.",
        "logoff":    "Logging off current user.",
    }

    if action not in commands:
        return jsonify({"status": "error", "message": "Unknown action."})

    try:
        subprocess.Popen(commands[action], shell=False)
        return jsonify({"status": "ok", "message": messages[action]})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed: {str(e)}"})


@app.route("/schedule", methods=["POST"])
def schedule_shutdown():
    data = request.get_json()
    minutes = data.get("minutes", 0)

    if not is_windows():
        return jsonify({
            "status": "error",
            "message": f"Only works on Windows (current OS: {platform.system()})"
        })

    try:
        seconds = int(minutes) * 60
        subprocess.Popen(["shutdown", "/s", "/t", str(seconds)], shell=False)
        return jsonify({
            "status": "ok",
            "message": f"Shutdown scheduled in {minutes} minute(s)."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed: {str(e)}"})


@app.route("/cancel", methods=["POST"])
def cancel_shutdown():
    if not is_windows():
        return jsonify({
            "status": "error",
            "message": f"Only works on Windows (current OS: {platform.system()})"
        })

    try:
        subprocess.Popen(["shutdown", "/a"], shell=False)
        return jsonify({"status": "ok", "message": "Scheduled shutdown cancelled."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed: {str(e)}"})


if __name__ == "__main__":
    # Run on all interfaces so it's accessible on the local network
    app.run(host="0.0.0.0", port=5000, debug=False)
