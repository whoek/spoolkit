"""

SpoolKit


"""
from flask import Flask, render_template, g
import time
import os
import sqlite3

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'sap_spoolkit.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))


# database usage
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.route("/")
def hello():
    db = get_db()
    c = db.execute('select date();')
    entries = c.fetchall()
    display_text = time.ctime()
    return render_template('index.html',
            display_text = display_text,
            entries = entries)

# open up browser
import webbrowser
webbrowser.open('http://localhost:9090/', new = 2)

# Run DEV server
if __name__ == "__main__":

# Build EXE
    app.run(port=9090, host='127.0.0.1', debug=True, use_reloader=False)
# DEBUG
#    app.run(port=9090, host='127.0.0.1', debug=True, use_reloader=True)



