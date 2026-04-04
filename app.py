"""
Team Falcons — UAV Telemetry Analyser
======================================
Run:
    pip install flask
    python app.py
Open: http://localhost:5000
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory store — cleared on every server restart (fulfils "gone on reload")
# Structure: { session_id: { filename, size_kb, timestamp_label, ... } }
SESSIONS = {}


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def handle_upload():
    """
    Receives the .bin file, stores minimal metadata in the server-side
    SESSIONS dict (no file bytes kept), and returns a session_id to
    the frontend so it can redirect after the fake loading bar finishes.

    Your team plugs the real parser here later — replace the placeholder
    block with: df = parse_bin(file.read()); metrics = compute_metrics(df); etc.
    """
    if "file" not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify(error="No file selected"), 400

    # ── PLACEHOLDER: real parsing goes here ────────────────────────────────
    file_bytes = file.read()          # read once so the stream isn't empty
    size_kb    = round(len(file_bytes) / 1024, 1)
    # ── END PLACEHOLDER ────────────────────────────────────────────────────

    session_id = str(uuid.uuid4())[:8]
    SESSIONS[session_id] = {
        "id":        session_id,
        "filename":  file.filename,
        "size_kb":   size_kb,
        "label":     file.filename.replace(".bin", "").upper(),
    }

    return jsonify(session_id=session_id)


@app.route("/dashboard")
def dashboard_home():
    """Dashboard with no active flight — shows empty state or last session."""
    return render_template("dashboard.html", session=None, all_sessions=list(SESSIONS.values()))


@app.route("/dashboard/<session_id>")
def dashboard_session(session_id):
    session = SESSIONS.get(session_id)
    if not session:
        return redirect(url_for("dashboard_home"))
    all_sessions = [s for s in SESSIONS.values() if s["id"] != session_id]
    return render_template("dashboard.html", session=session, all_sessions=all_sessions)


if __name__ == "__main__":
    app.run(debug=True, port=5000)