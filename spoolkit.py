"""
    Spoolkit
    :copyright: (c) 2017 by Willem Hoek.

    flash options:  
    success --> green
    info    --> blue
    warning --> orange
    danger -->  red


"""
from flask import Flask, render_template, g, request, Markup, jsonify, flash, redirect, url_for
import markdown
import time
import os
from os import listdir
from os.path import isfile, join, getsize, getctime
import sys
import sqlite3
import webbrowser

from flask_admin import Admin, BaseView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView

APP_PATH = os.path.abspath(".")          # application path

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)                 # change current working directory

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(APP_PATH, 'sap_spoolkit.db'),
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
    os.path.join(APP_PATH, 'sap_spoolkit.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    SECRET_KEY='F34TF$($e34Q',
    USERNAME='admin',
    PASSWORD='default',
    APP_PATH=APP_PATH,
    CWD_PATH=os.getcwd(),
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


def write_block(mode, block, table_count):
    """
    Used by insert tags 
    """
    if mode == '00':     # markdown
        html = markdown.markdown(block)
    elif mode == '01':   # sql
        try:
            result = db.engine.execute(block)
#            result = db.engine.execute("SELECT 'willem' as 'name', date('now') as 'date';")
            html = '<table id="table' + \
                str(table_count) + \
                '" class="table table-striped table-bordered" cellspacing="0" width="100%"><thead><tr>'
            for desc in result.cursor.description:
                html += '<th>' + str(desc[0]) + '</th>'
            html += '</tr></thead><tbody>'
            for row in result:
                html += '<tr>'
                for field in row:
                    html += '<td>' + str(field) + '</td>'
                html += '</tr>'
            html += '</tbody></table>'
#            html = block

        except Exception as e:
            html = '''<p class="bg-danger">''' + str(e) + '</p>'
    else:   # this should NOT happen
        pass
    return Markup(html)


def insert_tags(text):
    """
    returns the SQL table & markup text of a block of text

    mode 00 == Markdown  [DEFAULT]
    mode 01 == sql       SQL table
    mode 03 == snippit   [FUTURE USE]
    """
    mode = '00'     # default
    blankline_count = 0
    block = ''
    table_count = 0
    report = ''
    for line in text.split('\n'):
        try:
            line_no_spaces = str(line).replace(
                ' ', '').replace('\r', '').lower()
        except:
            line_no_spaces = line           # weird encoding

        if line_no_spaces == '--sql':
            report += write_block(mode, block, table_count)
            table_count += 1
            mode = '01'
            blankline_count = 0
            block = ''
        elif (line_no_spaces == '' and mode == '01') or line_no_spaces == '--text':
            blankline_count += 1
            if (blankline_count == 3 and mode == '01') or line_no_spaces == '--text':
                report += write_block(mode, block, table_count)
                mode = '00'
                blankline_count = 0
                block = ''
        else:
            block += line + '\n'
            blankline_count = 0
    report += write_block(mode, block, table_count)
    # report is html, table_count get used to adjust datatable JS in header
    return report, table_count

#######################################################################################
#
#  Flask - ROUTING
#
#######################################################################################

@app.route("/")
def root():
    reports = SpoolkitReports.query.all()
    return render_template('spoolkit_index.html',
                           reports=reports)

@app.route("/test")
def test():
    reports = SpoolkitReports.query.all()
    return render_template('spoolkit_test.html',
                           reports=reports)


@app.route("/r/<int:id>")
def view_report(id):
    report = SpoolkitReports.query.filter_by(id=id).first_or_404()
    md_text, table_count = insert_tags(report.script)
    table_count = range(1, table_count + 1)

    return render_template('spoolkit_report.html',
                           report=report,
                           md_text=md_text,
                           table_count=table_count,
                           )

@app.context_processor
def inject_now():
    return {'now': time.ctime()}


@app.route('/shutdown', methods=['GET'])   # GET = link,  POST = button
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return '''<br><br><br><br><h1>Thank you for using Spoolkit<br>
 Program shutting down... </h2><br>
        '''

@app.route('/loadfiles', methods=['GET'])   
def loadfiles():
    sapfiles = SpoolkitSapfiles.query.all()
    settings = SpoolkitSettings.query.filter_by(key='sapfile_dir').all()
    allfiles = []
    for setting in settings:
        mypath = setting.value
        t_directory = {}
        t_directory["directory"] = mypath
        onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
        t_allfiles = []
        for f in onlyfiles:
            t_file = {}
            t_file["filename"] = f
            t_file["fullfilename"] = str(os.path.join(mypath, f))
            t_file["filedate"] = str(time.ctime(getctime(mypath + '/' + f)))
            t_file["filesize"] = str(os.path.getsize(mypath + '/' + f)/1000000)
            ff = open(mypath + '/' + f,"r")
            head = [ff.readline() for i in range(100)]    # read first 100 line of file
            head = str(head).lower()
            ff.close()

            # check if any keyword is in any of files
            keyword_found = ''
            for sapfile in sapfiles:
                if sapfile.keyword.lower() in head:
                    keyword_found = sapfile.keyword.lower()
                    t_file["keyword"] = keyword_found

            t_file["column_field"] = ''
            t_file["database_table"] = ''
            t_allfiles.append(t_file)
        t_directory["files"] = t_allfiles
        allfiles.append(t_directory)            

    return render_template('spoolkit_sapfiles.html',
                           allfiles =   allfiles,
                           )

@app.route('/file_process', methods=['GET', 'POST'])
def file_process():
    if request.method == 'POST':
        data = request.form
        time.sleep(5)
        flash(str(data))
        return redirect(url_for('loadfiles'))
    else:
        flash("ERROR OCCURED -- TRY AGAIN")
        return redirect(url_for('loadfiles'))


@app.route('/_file_process_TEST')
def _file_process():
    try:
        dir = request.args.get('dir', '', type=str) 
        file = request.args.get('file', '', type=str) 
        keyword = request.args.get('keyword', '', type=str) 
        if keyword == 'willem':
            return jsonify(result='hello willem')
        else:
            return jsonify(result='not willem')
    except Exception as e:
        return str(e)

@app.route('/background_process')
def background_process():
    try:
        lang = request.args.get('proglang', 0, type=str)   
        time.sleep(5)
        if lang.lower() == 'python':
            return jsonify(result='You are wise')
        else:
            return jsonify(result='Try again.')
    except Exception as e:
        return str(e)


############################################################################
# SQLAlchemy
############################################################################


class SpoolkitSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50))
    value = db.Column(db.Text)


class SpoolkitReportgroups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)


class SpoolkitReports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(60))
    shortcode = db.Column(db.String(10))
    report_group = db.Column(db.String(10))
    connection = db.Column(db.String(50))
    script = db.Column(db.UnicodeText)
    cache_duration = db.Column(db.Integer, default=0)


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
    keyword = db.Column(db.String(50))
    header_field = db.Column(db.String(50))
    table_name = db.Column(db.String(50))
    pre_script = db.Column(db.Text)
    post_script = db.Column(db.Text)


class SpoolkitConnections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean)
    name = db.Column(db.Text)
    driver = db.Column(db.Text)
    host = db.Column(db.Text)
    port = db.Column(db.Integer)
    database = db.Column(db.Text)
    username = db.Column(db.Text)
    password = db.Column(db.Text)


db.create_all()

# Add some TEST entries
rec1 = SpoolkitReports(name='Show date', script='select date()', shortcode='1', is_active=True)
rec2 = SpoolkitReports(name='Show list of reports', script='select * from spoolkit_reports', shortcode='M2', is_active=True)
rec3 = SpoolkitReports(name='List of sap_files', script='select * from spoolkit_sapfiles', shortcode='K2', is_active=True)
db.session.add_all([rec1, rec2, rec3])
db.session.commit()

############################################################################
# flask-admin
############################################################################


class FileView(BaseView):
    @expose('/')
    def index(self):
#        return self.render('spoolkit_demo.html')
        return self.render('spoolkit_base.html')

class ReportView(ModelView):
    column_editable_list = ['is_active', 'shortcode']
    column_display_pk = True

class SapFileView(ModelView):
    #    column_editable_list = ['is_active', 'name']
    column_display_pk = True

#admin = Admin(app, name='Spoolkit', template_mode='bootstrap3', base_template='index2.html')
# Create admin with custom base template
admin = Admin(app, 'Datado', base_template='spoolkit_admin_layout.html', template_mode='bootstrap3')

admin.add_view(SapFileView(SpoolkitSapfiles, db.session, name='Define format', endpoint='filesetup', category='SAP Files'))
admin.add_view(FileView(name='Load', endpoint='loadfiles', category='SAP Files'))
admin.add_view(ReportView(SpoolkitReports, db.session, name='Setup', endpoint='setup', category='Reports'))
admin.add_view(FileView(name='Stats', endpoint='reportstats', category='Reports'))
admin.add_view(FileView(name='Cache', endpoint='reportcache', category='Reports'))
admin.add_view(ModelView(SpoolkitSettings, db.session, name='Settings', endpoint='appsettings', category='App'))
admin.add_view(FileView(name='Check Updates', endpoint='updates', category='App'))
admin.add_view(FileView(name='Help', endpoint='help', category='App'))
admin.add_view(FileView(name='Close', endpoint='close', category='App'))
admin.add_view(ModelView(SpoolkitUsers, db.session))

# open up browser
webbrowser.open('http://localhost:9090/', new=2)

# Run DEV server
if __name__ == "__main__":
    app.run(port=9090, host='0.0.0.0', debug=True, use_reloader=False)
