# Habit Tracker

A habit tracker with two front ends over one SQLite database:

- `app.py` - command line tool (argparse + sqlite3)
- `webapp.py` - Flask server exposing a JSON API and serving the web page
- `index.html` / `styles.css` / `app.js` - the browser front end
- `habit.bat` - Windows shortcut so `habit --list` works from anywhere

## Running it

```
py app.py --add "read"        # CLI
py app.py --log read
py app.py --stats all

py webapp.py                  # web app, then open http://127.0.0.1:5000
```

The database (`habits.db`) is not committed. It is created automatically the
first time you run `app.py`.
