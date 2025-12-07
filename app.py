from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "races.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            event_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            distance_label TEXT NOT NULL,
            time_str TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    print("DB initialized at", DB_PATH)


# inicializa o banco toda vez que o app for importado
init_db()


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def health():
    return jsonify({"status": "ok", "message": "Race API is running"})


@app.route("/api/races", methods=["OPTIONS"])
def races_options():
    return ("", 204)


@app.route("/api/races", methods=["POST"])
def add_race():
    data = request.get_json(force=True, silent=False)
    print("POST /api/races payload:", data)

    required = ["date", "event_name", "city", "country", "distance_label", "time_str"]
    if not all(field in data and str(data[field]).strip() for field in required):
        return jsonify({"error": "Missing required fields."}), 400

    date = data["date"].strip()
    event_name = data["event_name"].strip()
    city = data["city"].strip()
    country = data["country"].strip()
    distance_label = data["distance_label"].strip()
    time_str = data["time_str"].strip()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO races (date, event_name, city, country, distance_label, time_str)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (date, event_name, city, country, distance_label, time_str),
    )
    conn.commit()
    conn.close()

    print("Race inserted OK")
    return jsonify({"status": "ok"}), 201


@app.route("/api/races", methods=["GET"])
def list_races():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM races ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(
            {
                "id": row["id"],
                "date": row["date"],
                "event_name": row["event_name"],
                "city": row["city"],
                "country": row["country"],
                "distance_label": row["distance_label"],
                "time_str": row["time_str"],
            }
        )

    print("GET /api/races ->", result)
    return jsonify(result), 200


if __name__ == "__main__":
    # para rodar localmente, se você quiser testar:
    app.run(debug=True)
