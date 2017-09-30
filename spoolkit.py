"""
    Spoolkit
    :copyright: (c) 2017 by Willem Hoek.

"""
from flask import Flask, render_template, g, request
import time
import os
import sys
import sqlite3

# used by flask-admin
from flask_admin import  Admin, BaseView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView

APP_PATH = os.path.abspath(".")          # application path     

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)                 # change current working directory

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(APP_PATH, 'sap_spoolkit.db'),
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_PATH, 'sap_spoolkit.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS= True,
    SECRET_KEY='F34TF$($e34Q',
    USERNAME='admin',
    PASSWORD='default',
    APP_PATH = APP_PATH,
    CWD_PATH = os.getcwd(),
))

db = SQLAlchemy(app)   # used by flask-admin 

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
    c = db.execute('select * from spoolkit_reports')
    reports = c.fetchall()
    return render_template('spoolkit_index.html',
            reports = reports)

@app.route("/test")
def test():
    db = get_db()
    c = db.execute('select * from spoolkit_reports')
    reports = c.fetchall()
    return render_template('spoolkit_test.html',
            reports = reports)

@app.route("/r/<int:id>")
def view_report(id):
    db = get_db()
    sql = ('select * from spoolkit_reports where id = %s' % id)
    c = db.execute(sql)
    report = c.fetchone()
    sql_result = db.execute(report['body_script']) 
    return render_template('spoolkit_report.html',
            sql_result = sql_result,
            report = report )

@app.context_processor
def inject_now():
    return {'now': time.ctime() }

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET'])   # GET = link,  POST = button
def shutdown():
    shutdown_server()
    return '''<br><br><br><br><h1>Thank you for using Spoolkit<br>
 Program shutting down... </h2><br>
        '''
############################################################################
# SQLAlchemy
############################################################################

class SpoolkitSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

class SpoolkitReportgroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class SpoolkitReports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(60))
    shortcode = db.Column(db.String(10))
    report_group = db.Column(db.String(10))
    connection = db.Column(db.Text)
    pre_script = db.Column(db.Text)
    body_script = db.Column(db.Text)
    post_script = db.Column(db.Text)

class SpoolkitUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text)
    last_login = db.Column(db.DateTime)
    is_superuser = db.Column(db.Boolean) 
    username = db.Column(db.Text)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text)
    is_staff = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean)  
    date_joine = db.Column(db.DateTime)
    
class SpoolkitAuthUserPermissioins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer)

class SpoolkitSapfiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword =  db.Column(db.String(50))
    header_field = db.Column(db.String(50))
    table_name = db.Column(db.String(50))
    pre_script = db.Column(db.Text)
    post_script = db.Column(db.Text)

class SpoolkitConnections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)
    name = db.Column(db.Text)
    driver = db.Column(db.Text)
    host = db.Column(db.Text)
    port = db.Column(db.Integer)
    database = db.Column(db.Text)
    username = db.Column(db.Text)
    password = db.Column(db.Text)

db.create_all()

# Add some TEST entries
rec1 = SpoolkitReports(name= 'Show date', body_script = 'select date()', shortcode = '1')
rec2 = SpoolkitReports(name= 'Show list of reports', body_script = 'select * from spoolkit_reports', shortcode = 'M2')
rec3 = SpoolkitReports(name= 'List of sap_files', body_script = 'select * from spoolkit_sapfiles',shortcode = 'K2')
db.session.add_all([rec1, rec2, rec3])
db.session.commit()

############################################################################
# flask-admin
############################################################################

class FileView(BaseView):
    @expose('/')
    def index(self):
        return self.render('spoolkit_demo.html')
#        return self.render('spoolkit_base.html')

class ReportView(ModelView):
    column_editable_list = ['active', 'name','shortcode']
    column_display_pk = True

class SapFileView(ModelView):
#    column_editable_list = ['active', 'name']
    column_display_pk = True

#admin = Admin(app, name='Spoolkit', template_mode='bootstrap3', base_template='index2.html')
# Create admin with custom base template
#admin = Admin(app, 'Datado', base_template='spoolkit_admin_layout.html', template_mode='bootstrap3')
admin = Admin(app, 'Datado', template_mode='bootstrap3')

admin.add_view(SapFileView(SpoolkitSapfiles, db.session, name='Define format', endpoint='filesetup', category='SAP Files'))
admin.add_view(FileView(name='Load', endpoint='fileload', category='SAP Files'))
admin.add_view(ReportView(SpoolkitReports, db.session, name= 'Setup', endpoint='setup', category='Reports'))
admin.add_view(FileView(name='Stats', endpoint='reportstats', category='Reports'))
admin.add_view(FileView(name='Cache', endpoint='reportcache', category='Reports'))
admin.add_view(ModelView(SpoolkitSettings, db.session, name='Settings', endpoint='appsettings', category='App'))
admin.add_view(FileView(name='Check Updates', endpoint='updates', category='App'))
admin.add_view(FileView(name='Help', endpoint='help', category='App'))
admin.add_view(FileView(name='Close', endpoint='close', category='App'))

admin.add_view(ModelView(SpoolkitUsers, db.session))

# open up browser
import webbrowser
webbrowser.open('http://localhost:9090/', new = 2)

# Run DEV server
if __name__ == "__main__":
    app.run(port=9090, host='0.0.0.0', debug=True, use_reloader=False)
    