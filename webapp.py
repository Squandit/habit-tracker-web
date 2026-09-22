from pathlib import Path
import sqlite3
import datetime
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
    name = name.strip().title()
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

    return jsonify(ok=True), 200

@app.post('/api/log-habit')
def log_habit():
    data=request.get_json(silent=True) or {}
    habitid=data.get('id', '')
    date=datetime.date.today().isoformat()
    if not habitid:
        return jsonify({'error': 'Habit id is required'}), 400

    if not date:
        return jsonify({'error': 'Date is required'}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO log_habits (habit_id, completed_date) VALUES (?, ?)',
            (habitid, date)
        )
        db.commit()

    except sqlite3.Error as e:
        return jsonify({'error': 'SQLite error'}), 500

    return jsonify({'success': 'Logged'}), 200

@app.get('/api/get-habit-id')
def get_habit_id():
    name = request.args.get('name', '')
    if not name: 
        return jsonify({'error': 'Name is required'}), 400

    db = get_db()
    try:
        row = db.execute(
            'SELECT id FROM habits WHERE name = ?',
            (name,)
        ).fetchone()

    except sqlite3.Error as e:
        return jsonify({'error': 'SQLite error'}), 500

    if row is None:
        return jsonify({'error': 'habit not found'}), 404
    
    return jsonify({'id': row['id']}), 200

@app.get('/api/get-habit-completion')
def get_habit_completion():
    id = request.args.get('id', '')
    today=datetime.date.today().isoformat()
    if not id: 
        return jsonify({'error': 'Habit ID is required'}), 400

    db = get_db()
    try:
        row = db.execute(
            'SELECT completed_date FROM log_habits WHERE habit_id = ? AND completed_date = ?',
            (id, today)
        ).fetchone()

    except sqlite3.Error as e:
        return jsonify({'error': 'SQLite error'}), 500

    if row is None:
        return jsonify({'completed': False}), 200
    
    return jsonify({'completed': True}), 200


if __name__ == '__main__':
    app.run(debug=True)