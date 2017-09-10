"""

    Spoolkit
    :copyright: (c) 2017 by Willem Hoek.
"""
from flask import Flask, render_template, g
import time
import os
import sys
import sqlite3

# keep copy of application path and change working directory to EXE
# abspath => directory you run the EXE from
# sys.path => user\temp directory _MAIPASS
APP_PATH = os.path.abspath(".")          # application path     

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)                 # change current working directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(APP_PATH, 'sap_spoolkit.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    APP_PATH = APP_PATH,
    CWD_PATH = os.getcwd()
))

def init_db():
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        print 'init db.....', app.config['DATABASE']
        c = conn.cursor()
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name in ('configuration', 'reports')")
        count = c.fetchone()#[0]
        conn.close()
        if count[0] == 2:  # tables are there!!!
            return 0       # key tables found -- all OK
        else:
            raise Error
    except:
        return run_script('schema.sql')
    
def run_script(script_name):
    try:
        # read script
        script_file = os.path.join(app.config['CWD_PATH'],'sql', script_name)
        print 'script file: ', script_file
        fd = open(script_file, 'r')
        script = fd.read()
        fd.close()
    except:
        return 1
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.executescript(script)
        conn.commit()
        conn.close()
    except:
        return 2
    return 0

#print run_script('schema.sql')

# database usage
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().executescript(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def root():
    db = get_db()
    c = db.execute('select * from reports')
    reports = c.fetchall()
    display_text = time.ctime()
    return render_template('index.html',
            display_text = display_text,
            reports = reports)

@app.route("/r/<int:uid>")
def view_report(uid):
    db = get_db()
    sql = ('select * from reports where uid = %s' % uid)
    c = db.execute(sql)
    report = c.fetchone()
    display_text = time.ctime()
    return render_template('report.html',
            display_text = display_text,
            report = report )

# ============================================================================
#
# MAIN APPLICATION
#
# ============================================================================

init_db()

# open up browser
import webbrowser
webbrowser.open('http://localhost:9090/', new = 2)

# Run DEV server
if __name__ == "__main__":
    app.run(port=9090, host='0.0.0.0', debug=True, use_reloader=False)
    

