from pathlib import Path
import sqlite3
from flask import Flask, g, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR
DATABASE = BASE_DIR / 'habits.db'

app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path='')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.get('/')
def index():
    return send_from_directory(WEB_DIR, 'index.html')

@app.get('/api/habits-list')
def get_habits_list():
    habits = get_db().execute(
        'SELECT id, name, description FROM habits ORDER BY id'
    ).fetchall()
    return jsonify(habits=[dict(habit) for habit in habits])


@app.post('/api/add-habit')
def add_habit():
    data=request.get_json(silent=True) or {}
    name = data.get('name', '')
    description = data.get('description', '') or None
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO habits (name, description) VALUES (?, ?)',
            (name, description)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Habit with this name already exists'}), 409

    return jsonify(ok=True), 201