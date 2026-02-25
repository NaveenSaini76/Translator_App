"""
app.py — Flask backend for the AI Translator Web Application.
Run with:  python app.py
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, jsonify

# Our custom translation module (no API key required)
from utils.translator import translate_text, get_language_list, detect_language

# ---------------------------------------------------------------------------
# Flask App Initialisation
# ---------------------------------------------------------------------------
app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), "database.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    """Open a new SQLite connection and return it."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def init_db():
    """Create the translation_history table if it doesn't exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS translation_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text TEXT    NOT NULL,
            translated  TEXT    NOT NULL,
            source_lang TEXT    NOT NULL,
            target_lang TEXT    NOT NULL,
            detected    TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# Create table on startup
init_db()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main page."""
    languages = get_language_list()
    return render_template("index.html", languages=languages)


@app.route("/translate", methods=["POST"])
def translate():
    """
    AJAX endpoint — receives JSON {text, source, target} and returns
    the translation result.
    """
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    source = data.get("source", "auto")
    target = data.get("target", "en")

    if not text:
        return jsonify({"success": False, "error": "Please enter some text to translate."})

    result = translate_text(text, source, target)

    # Save to history on success
    if result["success"]:
        conn = get_db()
        conn.execute(
            """INSERT INTO translation_history
               (source_text, translated, source_lang, target_lang, detected, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                text,
                result["translated_text"],
                source,
                target,
                result["detected_language"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        conn.close()

    return jsonify(result)


@app.route("/history")
def history():
    """Return the last 20 translation history records as JSON."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM translation_history ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/clear-history", methods=["POST"])
def clear_history():
    """Delete all translation history."""
    conn = get_db()
    conn.execute("DELETE FROM translation_history")
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/detect", methods=["POST"])
def detect_lang():
    """Detect the language of provided text."""
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"detected": "unknown"})
    return jsonify({"detected": detect_language(text)})


# ---------------------------------------------------------------------------
# Run the development server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n✨  AI Translator is running at  http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
