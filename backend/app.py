from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return jsonify({"success": True, "message": f"Logged in for {data.get('warehouse')}"})

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