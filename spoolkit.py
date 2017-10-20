"""
    Spoolkit
    :copyright: (c) 2017 by Willem Hoek.

"""
import  email.mime.message, email.mime.image, email.mime.text, email.mime.multipart, email.mime.audio
from flask import Flask, render_template, g, request, Markup, jsonify, flash, redirect, url_for
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import markdown
import os
from os import listdir
from os.path import isfile, join, getsize, getctime
import sqlite3
import string
import shutil
import subprocess
import sys
import time
import timeit
import webbrowser

DB_FILE = 'sap_spoolkit.db'
SAP_DIR = 'sapdir'
DELIMIT = '|'
MAX_SEARCH = 100    # after __ lines, stop searching for key or header field
START = 0
GOT_KEY = 1
GOT_HEADER = 2

# APP_PATH is where DB should be saved. Same as .py or EXE
if getattr(sys, 'frozen', False):
    APP_PATH = os.path.dirname(sys.executable).replace('\\','/')
    os.chdir(sys._MEIPASS)                 # change current working directory
elif __file__:
    APP_PATH = os.path.dirname(__file__).replace('\\','/')

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(APP_PATH, DB_FILE).replace('\\','/'),
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
        os.path.join(APP_PATH, DB_FILE).replace('\\','/'),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    SECRET_KEY='F34TF$($e34Q',
    USERNAME='admin',
    PASSWORD='default',
    VERSION = '0.3',
    APP_PATH=APP_PATH, 
    CWD_PATH=os.getcwd().replace('\\','/'),
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

        except Exception as e:
            html = '''<p class="bg-danger">''' + str(e) + '</p>'
    else:   # this should NOT happen
        pass
    return Markup(html)


def insert_tags(text):
    """
    returns the SQL table & markup text of a block of text

    mode 00 -- text //  Markdown  [DEFAULT]
    mode 01 -- sql       SQL table
    mode 02 -- file      (XLS file -- FUTURE USE)
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


###############################################################################
# Load file
###############################################################################

def make_field_unique(f1, field):
    """ Make sure the field is not same as already used field
    If it is same make the field z1, z2,.....etc
    """
    unique = 0
    c = 1
    field = string.lower(field)
    if f1 == [] and field == '':
        field = 'z1'
    while not unique:
        unique = 1
        for f in f1:
            if field == string.lower(f) or field == '':
                field = 'z' + str(c)
                c += 1
                unique = 0
    return field

def create_sqlite_table(status):
    sql = 'create table %s ( \n "' % (status["table_name"],)
    sql += '"  text, \n "'.join(status["header_fields"])
    sql += '"  text \n); \n\n'
    return sql


def get_fields(splitline):
    ft = []     # field_tuple, "(field1, field2, ...)"
    # build tuple of all fields
    for field in splitline:
        field = string.strip(field)
        #TODO   only allow ascii
        #TODO   start with CHAR not number
        invalid_chars = "\/~!@#$%^&*()+- .,'`|{}?<>;:"
        for c in invalid_chars:
            field = string.replace(field,c,"")
        field = make_field_unique(ft, field)   # ft = columns to date, field = new
        ft.append(string.strip(field))
    return tuple(ft)

def ensure_dir(file_path):
    """
    http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def fileload_sqlite(fullfilename, sapfile_setup):
    """
    """
    step = START    

    status = {}
    start_time = timeit.default_timer()
    linenum = 0

    try:
        input = file(os.path.abspath(fullfilename).replace('\\','/'))
        status["mypath"] = os.path.dirname(fullfilename).replace('\\','/')
        status["myfile"] = os.path.basename(fullfilename).replace('\\','/')

        csvfile = APP_PATH + '/temp/' + status["myfile"]
        ensure_dir(csvfile)
        csv = open(csvfile, 'w')

        #f = codecs.open(os.path.abspath(input_file), "r",encoding='ascii')
        for line in input.readlines():
            linenum += 1
            # remove all non-ascii characters
            line = string.replace(line,"\\","").strip()

            try:
                line = line.encode('utf8', 'replace')
                line = line.encode('ascii', 'replace')
            except:
                line = ''.join([i if ord(i) < 128 else '#' for i in line])

            if step == GOT_HEADER:
                splitline = string.splitfields(line,DELIMIT)
                splitline_len = len(splitline)
                if splitline_len < status["header_fields_count"]:
                    missing = field_len - splitline_len
                    splitline.extend(['' for i in missing*'-'])
                s = "\t".join(str(x).strip(' \t\n') for x in splitline[0:field_len]) + '\n'
                csv.write(s)

            elif step == START:
                for sapfile in sapfile_setup:
                    if sapfile.keyword.lower() in line.lower():     # found KEYWORD                        
                        status["linenum_keyword"] = linenum
                        status["keyword"] = sapfile.keyword.lower()
                        step = GOT_KEY
                    elif linenum > MAX_SEARCH:
                        break

            elif step == GOT_KEY:
                for sapfile in sapfile_setup:
                    # both KEYWORD and HEADER_FIELD must match
                    if (sapfile.keyword.lower() == status.get("keyword")) and \
                    (sapfile.header_field.lower() in line.lower()):
                        status["header_field"] = sapfile.header_field.lower()
                        status["linenum_header_field"] = linenum
                        status["table_name"] = sapfile.table_name.lower()
                        splitline = string.splitfields(line,DELIMIT)
                        status["header_fields_init"] = splitline
                        status["header_fields"] = get_fields(splitline)
                        status["header_fields_count"] = len(status["header_fields"])
                        field_len = status["header_fields_count"]
                        s = "\t".join(str(x).strip(' \t\n') for x in status["header_fields"]) + '\n'              
                        status["s"] = s
                        step = GOT_HEADER

                    elif linenum > MAX_SEARCH:
                        break

        status["linenum_end"] = linenum
        input.close()
        csv.close()
        
        if "header_fields_count" in status:
            sql_db = app.config['DATABASE']
            sql_drop = "drop table if exists {};\n\n".format(status["table_name"])
            sql_create = create_sqlite_table(status)
            sql_import = ".import '{}'  '{}' ".format(csvfile, status["table_name"])
            
            # subprocess starting now
            sql_result = subprocess.call(["sqlite3.exe", sql_db, 
                sql_drop, sql_create, ".separator \t",sql_import])  

            status["sql_db"] = sql_db
            status["sql_result"] = sql_result
            status["sql_drop"] = sql_drop
            status["sql_create"] = sql_create
            status["sql_import"] = sql_import

            try:
                pass
#                os.remove(csvfile)
            except:
                pass    #else delete it when program start up again

            if sql_result == 0:
                #when done, move the TXT file to archive
                to_path = status["mypath"] + '/archive/' + time.strftime('%Y_%m_%d')
                to_file = to_path + '/' + str(status["myfile"])
                status["to_path"] = to_path
                ensure_dir(to_file)
                shutil.move(fullfilename, to_file)
#                shutil.copy(fullfilename, to_file)

    # write summary in a log file and return ID

    except IOError as e:
        status["error"] = "({})".format(e)

    status["duration"] = str(timeit.default_timer() - start_time)
    return status

def fileload_success_message(status):
    message = """
    <h4><samp>File {myfile} loaded in table {table_name}</samp></h4><br>

<div class="row">
    <div class="col-md-2">Rows</div>
    <div class="col-md-10"><samp>{linenum_end}</samp></div>
</div>
<div class="row">
    <div class="col-md-2">Fields</div>
    <div class="col-md-10"><samp>{header_fields_count}</samp></div>
</div>
<div class="row">
    <div class="col-md-2">Keyword in line {linenum_keyword}</div>
    <div class="col-md-10"><samp>{keyword}</samp></div>
</div>

<div class="row">
    <div class="col-md-2">Header field in line {linenum_header_field}</div>
    <div class="col-md-10"><samp>{header_field}</samp></div>
</div>
<div class="row">
    <div class="col-md-2">Moved file to</div>
    <div class="col-md-10"><samp>{to_path}/</samp></div>
</div>

<br><div>All done in {:.3} seconds</div>
{sql_result}
    
    """.format(float(status.get("duration")), **status )
    return message

#######################################################################################
#
#  Flask - ROUTING
#
#######################################################################################

@app.route("/")
def root():
#    reports = SpoolkitReports.query.all()
    reports = SpoolkitReports.query.filter_by(is_active=1).all()
    
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
    try:
        sapfile_setup = SpoolkitSapfiles.query.order_by(SpoolkitSapfiles.id).all()
        sapfile_dir = SpoolkitSettings.query.filter_by(key=SAP_DIR).all()
        allfiles = []
        id = ''
        for sapdir in sapfile_dir:
            mypath = sapdir.value
            t_directory = {}
            t_directory["directory"] = mypath
            id = sapdir.id
            t_directory["id"] = sapdir.id
            file_list = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
            t_allfiles = []
            for f in file_list:
                t_file = {}
                t_file["filename"] = f
                t_file["fullfilename"] = str(os.path.join(mypath, f).replace('\\','/'))
                t_file["filedate"] = str(time.ctime(getctime(mypath + '/' + f)))
                filesize = os.path.getsize(mypath + '/' + f)
                if filesize < 1000000:
                    t_file["filesize"] = '<1'
                else:
                    t_file["filesize"] = '{:,}'.format( filesize/1000000 ) 
                # get first 100 lines of file
                ff = open(mypath + '/' + f,"r")
                head = [ff.readline() for i in range(100)]    
                head = str(head).lower()
                ff.close()

############## LOOK FOR FIELDS - start ##############

                linenum = 0
                step = START
                input = file(os.path.abspath(mypath + '/' + f).replace('\\','/'))
                for line in input.readlines():
                    linenum += 1
                    # remove all non-ascii characters
                    line = string.replace(line,"\\","").strip()
                    try:
                        line = line.encode('utf8', 'replace')
                        line = line.encode('ascii', 'replace')
                    except:
                        line = ''.join([i if ord(i) < 128 else '#' for i in line])

                    if step == START:
                        for sapfile in sapfile_setup:
                            if sapfile.keyword.lower() in line.lower():     # found KEYWORD                        
                                t_file["keyword"] = sapfile.keyword.lower()
                                step = GOT_KEY
                            elif linenum > MAX_SEARCH:
                                break

                    elif step == GOT_KEY:
                        for sapfile in sapfile_setup:
                            # both KEYWORD and HEADER_FIELD must match
                            if (sapfile.keyword.lower() == t_file.get("keyword")) and \
                            (sapfile.header_field.lower() in line.lower()):
                                t_file["header_field"] = sapfile.header_field.lower()
                                t_file["table_name"] = sapfile.table_name.lower()
                                break

                            elif linenum > MAX_SEARCH:
                                break

############## LOOK FOR FIELDS - end ##############

                t_allfiles.append(t_file)
            t_directory["files"] = t_allfiles
            allfiles.append(t_directory)            
    except Exception as e:
        id = id
        new_url = '/admin/appsettings/edit/?url=%2Fadmin%2Fappsettings%2F&id={}'.format(id)
        message = str(e) + '<br><br>Check in <strong>Value</strong> field below if directory is correct<br>'
        flash(Markup(message), 'danger')
        return redirect(new_url)

    return render_template('spoolkit_sapfiles.html',
                           allfiles =   allfiles,
                           )


@app.route('/file_process', methods=['GET', 'POST'])
def file_process():
    """
    Flash Categories: success (green), info (blue), warning (yellow), danger (red) 
    """
    if request.method == 'POST':
        sapfile_setup = SpoolkitSapfiles.query.order_by(SpoolkitSapfiles.id).all()      
        fullfilename  = request.form.get("fullfilename")
        if fullfilename is None:
            message = Markup("<h4>No file was selected</h4>")
            flash(message,'danger')
        else:
            status = fileload_sqlite(fullfilename, sapfile_setup)
            if status.get("sql_result") == 0:
                message = Markup(fileload_success_message(status))
                flash(message, 'success')
#                flash(status, 'success')
            else:
                flash(str(status), 'danger')
        return redirect(url_for('loadfiles'))
    else:
        flash("ERROR OCCURED -- TRY AGAIN", 'danger')
        return redirect(url_for('loadfiles'))


@app.route('/display_file', methods=['GET'])
def display_file():
    """
    Display TXT file in Flash Categories: success (green), info (blue), warning (yellow), danger (red) 
    """
    try:
        filename = request.args.get('filename')
        keyword = request.args.get('keyword')
        header_field = request.args.get('header_field')
        table_name = request.args.get('table_name')        
        input = file(filename)
        linenum = 0
        top100 = ''

        for line in input.readlines():
            linenum += 1
            line = string.replace(line,"\\","").strip()
            try:
                line = line.encode('utf8', 'replace')
                line = line.encode('ascii', 'replace')
            except:
                line = ''.join([i if ord(i) < 128 else '#' for i in line])

            top100 += '<kbd>{:03d}</kbd> {}<br>'.format(linenum, line)
            if linenum == 100:
                break
        input.close()
        top100 = Markup(top100)
    except Exception as e:
        message = str(e)
        flash(Markup(message), 'danger')
        return redirect(url_for('loadfiles'))

    return render_template('spoolkit_display_file.html',
            filename = filename.replace('/','\\'),
            keyword = keyword,
            header_field = header_field,
            table_name = table_name,
            top100 = top100,
            )

@app.route('/cd', methods=['GET'])
def change_sap_directory():
    """
    Change directory of files to be loaded
    """
    try:
        id = request.args.get('id')
        new_url = '/admin/appsettings/edit/?url=%2Fadmin%2Fappsettings%2F&id={}'.format(id)
    except:
        flash("ERROR OCCURED -- TRY AGAIN", 'danger')
        return redirect(url_for('loadfiles'))
    return redirect(new_url)


@app.route('/newdir', methods=['GET'])
def new_sap_directory():
    """
    New folder
    """
    try:
        entry = SpoolkitSettings(key=SAP_DIR, value='C:\Documents\SAP\SAP GUI')
        db.session.add_all([entry])
        db.session.commit()
        new_url = '/admin/appsettings/edit/?url=%2Fadmin%2Fappsettings%2F&id={}'.format(entry.id)
    except:
        flash("ERROR OCCURED -- TRY AGAIN", 'danger')
        return redirect(url_for('loadfiles'))
    return redirect(new_url)


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
    name = db.Column(db.String(60), nullable=False)
    shortcode = db.Column(db.String(10))
    report_group = db.Column(db.String(10))
    connection = db.Column(db.String(50))
    script = db.Column(db.UnicodeText, nullable=False)
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
    keyword = db.Column(db.String(50), nullable=False)
    header_field = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
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
db.session.add_all([rec1])
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
    column_editable_list = ['is_active', 'name']
    column_display_pk = True
    column_exclude_list = ('report_group', 'connection', 'cache_duration','shortcode')
    column_labels = dict(id='ID', is_active='Active', name='Report name', 
        shortcode='Shortcode',script='Report contents',
        )
    column_descriptions = dict(
        script='Report contents can either be --text or --sql',
        shortcode='Quick access of reports [DEACTIVE]',
        cache_duration='Time in seconds before report will be recalculated [DEACTIVE]',
        )

class SapFileView(ModelView):
    column_display_pk = True
    column_editable_list = ['keyword', 'header_field','table_name']
    column_descriptions = dict(
        keyword='Field in file to uniquely identify type of file',
        header_field='Field in file to identify the field names',
        table_name='Database table name where data will be loaded',
        pre_script='SQL statement that will run BEFORE the data is loaded',
        post_script='SQL statement that will run AFTER the data was loaded',
        )

# Create admin with custom base template
admin = Admin(app, '', base_template='spoolkit_admin_layout.html', template_mode='bootstrap3')
admin.add_view(SapFileView(SpoolkitSapfiles, db.session, name='Define format', endpoint='filesetup', category='SAP Files'))
admin.add_view(ReportView(SpoolkitReports, db.session, name='Setup', endpoint='setup', category='Reports'))
admin.add_view(ModelView(SpoolkitSettings, db.session, name='Settings', endpoint='appsettings', category='App'))
admin.add_view(ModelView(SpoolkitUsers, db.session))

# Open browser and Run DEV server
if __name__ == "__main__":
    webbrowser.open('http://localhost:9119/', new=2)
    app.run(port=9119, host='0.0.0.0', debug=True, use_reloader=True)
