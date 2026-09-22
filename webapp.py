from pathlib import Path
import sqlite3
import datetime
from flask import Flask, g, jsonify, request, send_from_directory

# BASE_DIR = the folder this file lives in, so paths work no matter where
# the script gets run from. WEB_DIR is the same folder, used to serve the
# frontend files (index.html, app.js, styles.css). DATABASE is the path to
# the SQLite file all the routes below read from and write to.
BASE_DIR = Path(__file__).parent
WEB_DIR = BASE_DIR
DATABASE = BASE_DIR / 'habits.db'

# static_folder + static_url_path='' means Flask serves any file in
# WEB_DIR (app.js, styles.css, etc) directly at the root URL, e.g.
# /app.js instead of /static/app.js.
app = Flask(__name__, static_folder=str(WEB_DIR), static_url_path='')


def get_db():
    # 'g' is Flask's per-request storage object. This pattern opens ONE
    # database connection per request and reuses it for every query that
    # request makes, instead of opening a new connection every time.
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        # row_factory = sqlite3.Row lets you read columns by name
        # (row['name']) instead of only by index (row[0]).
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    # Runs automatically after every request finishes, success or error.
    # Closes the connection opened in get_db() so connections don't pile up.
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.get('/')
def index():
    # Serves the actual index.html page when someone visits the site root.
    return send_from_directory(WEB_DIR, 'index.html')

@app.get('/api/habits-list')
def get_habits_list():
    # Called by app.js on page load to get every habit, plus whether
    # each one has already been logged today.
    today = datetime.date.today().isoformat()
    habits = get_db().execute(
        # The EXISTS(...) subquery runs once per habit row (that's what
        # "habits.id" inside it refers back to) and checks whether a
        # log_habits row exists for that habit on today's date. Comes
        # back as 1 or 0, aliased as done_today.
        'SELECT id, name, description, EXISTS(SELECT 1 FROM log_habits WHERE log_habits.habit_id = habits.id AND log_habits.completed_date = ?) AS done_today FROM habits ORDER BY id',
        (today,)
    ).fetchall()
    return jsonify(habits=[dict(habit) for habit in habits])


@app.post('/api/add-habit')
def add_habit():
    # Called when the "+ Add Habit" form gets submitted.
    data=request.get_json(silent=True) or {}
    name = data.get('name', '')
    # Normalize before storing so "running" and "Running" count as the
    # same habit for the UNIQUE constraint below, and so it always
    # displays the same way regardless of how it was typed.
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
        # Fires if habits.name has a UNIQUE constraint and this name
        # already exists.
        return jsonify({'error': 'Habit with this name already exists'}), 409

    return jsonify(ok=True), 200

@app.post('/api/log-habit')
def log_habit():
    # Called when a checkbox gets ticked, marks that habit done for today.
    data=request.get_json(silent=True) or {}
    habitid=data.get('id', '')
    # Date is computed here, server-side, rather than trusting whatever
    # the browser's clock says, so it's always "today" from the server's
    # point of view.
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

@app.delete('/api/log-habit')
def unlog_habit():
    


if __name__ == '__main__':
    # Only runs the dev server when this file is executed directly
    # (py webapp.py), not when it's imported elsewhere.
    app.run(debug=True)
