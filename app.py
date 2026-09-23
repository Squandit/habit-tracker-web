import sqlite3
import argparse
from datetime import datetime

connection = sqlite3.connect('habits.db')
cursor = connection.cursor()

habits = """CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""

cursor.execute(habits)

log_habits = """CREATE TABLE IF NOT EXISTS log_habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_date DATE NOT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits (id)
)"""

cursor.execute(log_habits)

# CLI

def create_parser():
    parser = argparse.ArgumentParser(description="Multi-argument CLI tool.")

    parser.add_argument('--log', nargs='+', help='List of items to log')
    parser.add_argument('--add', type=str, help='Item to add')
    parser.add_argument('--list', action='store_true', help='List all habits')
    parser.add_argument('--today', action='store_true', help="List today's logged habits")
    parser.add_argument('--all-time', action='store_true', help="List all-time logged habits")
    parser.add_argument('--stats', type=str, help="Show stats for a habit")
    return parser

def main():
    args = create_parser().parse_args()

    if args.log:
        for item in args.log:
            log_habit(item.strip().lower())

    if args.add:
        for item in args.add.split(','):
            add_habit(item.strip().lower())

    if args.list:
        list_habits()

    if args.today:
        print_table("Today's habits", ["Habit", "Date", "Times"], habits_today())

    if args.all_time:
        print_table("All-time habits", ["Habit", "Times"], all_time())

    if args.stats:
        stats(args.stats.strip().lower())

# habit actions

def stats(habit_name):
    if habit_name != "all":
        cursor.execute("""
            SELECT habits.name,
                   habits.created_at,
                   COUNT(log_habits.id),
                   MAX(log_habits.completed_date)
            FROM habits
            LEFT JOIN log_habits ON habits.id = log_habits.habit_id
        WHERE habits.name = ?
        GROUP BY habits.id, habits.name, habits.created_at
    """, (habit_name,))
    habit_stats = cursor.fetchone()

    if habit_stats:
        habit_stats = [add_completion_percentage(habit_stats)]
        print_table(
            f"Stats for {habit_name}",
            ["Habit", "Created", "Completions", "Last completed", "Completion %"],
            habit_stats
        )
    elif habit_name == "all":
        cursor.execute("""
            SELECT habits.name,
                   habits.created_at,
                   COUNT(log_habits.id),
                   MAX(log_habits.completed_date)
            FROM habits
            LEFT JOIN log_habits ON habits.id = log_habits.habit_id
            GROUP BY habits.id, habits.name, habits.created_at
        """)
        all_stats = cursor.fetchall()
        all_stats = [add_completion_percentage(habit) for habit in all_stats]
        print_table(
            "Stats for all habits",
            ["Habit", "Created", "Completions", "Last completed", "Completion %"],
            all_stats
        )
    else:
        print(f"No stats found for habit '{habit_name}'. Please add it first.")

def add_completion_percentage(habit_stats):
    name, created_at, completions, last_completed = habit_stats
    created_date = datetime.strptime(created_at[:10], "%Y-%m-%d").date()
    today = datetime.now().date()
    days_since_creation = max((today - created_date).days + 1, 1)
    completion_percentage = round(completions / days_since_creation * 100, 1)

    return [name, created_date, completions, last_completed or "Never", f"{completion_percentage}%"]

def log_habit(habit_name):
    cursor.execute("SELECT id FROM habits WHERE name = ?", (habit_name,))
    habit = cursor.fetchone()

    if habit:
        habit_id = habit[0]
        completed_date = datetime.now().date().isoformat()

        logged_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO log_habits (habit_id, completed_date, logged_at)
            VALUES (?, ?, ?)
        """, (habit_id, completed_date, logged_at))
        connection.commit()

        cursor.execute("""
            SELECT habits.name
            FROM habits
            WHERE habits.id NOT IN (
                SELECT habit_id
                FROM log_habits
                WHERE completed_date = ?
            )
        """, (completed_date,))
        not_completed = cursor.fetchall()

        rows = [
            f"Logged habit: {habit_name} on {completed_date}",
            "Not completed today:"
        ]
        rows.extend(f"  - {habit[0]}" for habit in not_completed)
        width = max(len(row) for row in rows)

        print(f"┌{'─' * width}┐")
        print(f"│{rows[0]:<{width}}│")
        print(f"├{'─' * width}┤")
        for row in rows[1:]:
            print(f"│{row:<{width}}│")
        print(f"└{'─' * width}┘")

    else:
        print(f"Habit '{habit_name}' does not exist. Please add it first.")

def add_habit(name, description=None):
    try:
        cursor.execute("INSERT INTO habits (name, description) VALUES (?, ?)", (name, description))
        connection.commit()
        print(f"Added habit: {name}")
    except sqlite3.IntegrityError:
        print(f"Habit '{name}' already exists.")

# Reports

def habits_today():
    cursor.execute("""
        SELECT habits.name, log_habits.completed_date, COUNT(log_habits.id) as log_count
        FROM log_habits
        JOIN habits ON habits.id = log_habits.habit_id
        WHERE log_habits.completed_date = ?
        GROUP BY habits.name, log_habits.completed_date
    """, (datetime.now().date().isoformat(),))
    habits = cursor.fetchall()
    habits = [[habit[0], habit[1], habit[2]] for habit in habits]
    return habits

def all_time():
    cursor.execute("""
        SELECT habits.name, COUNT(log_habits.id) as log_count
        FROM log_habits
        JOIN habits ON habits.id = log_habits.habit_id
        GROUP BY habits.name
    """)
    habits = cursor.fetchall()
    habits = [[habit[0], habit[1]] for habit in habits]
    return habits

def list_habits():
    cursor.execute("SELECT * FROM habits")
    habits = cursor.fetchall()
    print_table("All habits", ["ID", "Name", "Description", "Created"], habits)

# Output

def print_table(title, headers, rows):
    """Print rows as a table whose column widths adapt to the content."""
    rows = [["" if value is None else str(value) for value in row] for row in rows]
    headers = [str(header) for header in headers]
    widths = [len(header) for header in headers]

    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def border(left, middle, right, fill="─"):
        sections = [fill * (width + 2) for width in widths]
        return left + middle.join(sections) + right

    def row_line(values):
        cells = [f" {value:<{width}} " for value, width in zip(values, widths)]
        return "│" + "│".join(cells) + "│"

    print(title)
    print(border("┌", "┬", "┐"))
    print(row_line(headers))
    print(border("├", "┼", "┤"))
    for row in rows:
        print(row_line(row))
    print(border("└", "┴", "┘"))

# we love you if name == main
if __name__ == '__main__':
    main()