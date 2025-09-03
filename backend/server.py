from flask import Flask, jsonify, request
import json
import subprocess
import os

app = Flask(__name__)

STATUS_FILE = "flex_auth_status.json"

def read_auth_status():
    try:
        with open(STATUS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"authenticated": False, "message": "No status file yet."}
    except json.JSONDecodeError:
        return {"authenticated": False, "message": "Corrupt status file."}

@app.route('/auth_status', methods=['GET'])
def auth_status():
    return jsonify(read_auth_status())

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    warehouse = data.get("warehouse", "Default")

    try:
        # Run flex.auth.py as a subprocess
        result = subprocess.run(
            ["python", "flex.auth.py"],
            capture_output=True,
            text=True,
            timeout=180  # prevent hang forever
        )
        print("Auth bot output:\n", result.stdout)
        if result.stderr:
            print("Auth bot error:\n", result.stderr)
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "message": "Login timed out"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {e}"}), 500

    return jsonify({"success": True, "message": f"Login attempt started for {warehouse}"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify({
        "blocksGrabbed": 5,
        "earnings": 125.50,
        "history": [
            {"date": "Day 1", "earnings": 50.00},
            {"date": "Day 2", "earnings": 75.50},
            {"date": "Day 3", "earnings": 125.50}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
