"""

SpoolKit
Willem Hoek
2017 @ Matimba Ventures Pty Ltd

"""
from flask import Flask, render_template, g
import time
import os
import sys
import sqlite3

# abspath => directory you run the EXE from
# sys.path => user\temp directory _MAIPASS

# keep this on top 
APP_PATH = os.path.abspath(".")          # application path     

# change working directory to _MEIPASS for single EXE
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)                 # change current working directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(APP_PATH, 'sap_spoolkit.db'),
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


def query_db(query, args=(), one=False):
    cur = get_db().executescript(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def hello():
    db = get_db()
    c = db.execute('select date();')
    entries = c.fetchall()
    display_text = time.ctime()
    return render_template('index.html',
            display_text = display_text,
            entries = entries)


# ============================================================================
#
# MAIN APPLICATION
#
# ============================================================================

# Open and read the file as a single buffer
#@app.before_first_request
#def load_schema():
#    fd = open('sql/schema.sql', 'r')
#    sqlFile = fd.read()
#    query_db(sqlFile)
#    fd.close()

# open up browser
import webbrowser
webbrowser.open('http://localhost:9090/', new = 2)

# Run DEV server
if __name__ == "__main__":
    app.run(port=9090, host='127.0.0.1', debug=True, use_reloader=False)
    

