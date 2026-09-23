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

py webapp.py                  # web app, then open http://localhost:5000
```

The database (`habits.db`) is not committed. It is created automatically the
first time you run `app.py`, so first run `python app.py --help` to create the db

The theme is Catppuccin Mocha, defined in the `@theme` block in
`src/input.css`. Change the hexes there and every utility follows.
