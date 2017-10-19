import timeit
import os
import string
import time
import datetime
import shutil
from os import listdir
from os.path import isfile, join, getsize, getctime
import sys
import subprocess

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

    DELIMIT = '|'
    MAX_SEARCH = 100    # after __ lines, stop searching for key or header field
    START = 0
    GOT_KEY = 1
    GOT_HEADER = 2
    step = START    

    status = {}
    start_time = timeit.default_timer()
    linenum = 0

    try:
        input = file(os.path.abspath(fullfilename))
        status["mypath"] = os.path.dirname(fullfilename)
        status["myfile"] = os.path.basename(fullfilename)

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
                # http://stackoverflow.com/questions/2743070/removing-non-ascii-characters-from-a-string-using-python-django
                stripped = stripped = (c for c in line if 0 < ord(c) < 127)
                line = ''.join(stripped)

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
                    if sapfile["keyword"].lower() in line.lower():     # found KEYWORD                        
                        status["linenum_keyword"] = linenum
                        status["keyword"] = sapfile["keyword"].lower()
                        step = GOT_KEY
                    elif linenum > MAX_SEARCH:
                        break

            elif step == GOT_KEY:
                for sapfile in sapfile_setup:
                    if sapfile["header_field"].lower() in line.lower():
                        # Found HEADER
                        status["header_field"] = sapfile["header_field"].lower()
                        status["linenum_header_field"] = linenum
                        status["table_name"] = sapfile["table_name"].lower()
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
            sql_drop = "drop table if exists %s;\n\n" % (status["table_name"],)
            sql_create = create_sqlite_table(status)
            sql_import = ".import {}  {} ".format(csvfile, status["table_name"])
            
            # subprocess starting now
            result = subprocess.call(["sqlite3.exe",  "sap_spoolkit.db", 
                sql_drop, sql_create, ".separator '\t'",sql_import])  

            # delete the CSV file in temp directory
            try:
                os.remove(csvfile)
            except:
                pass    #else delete it when program start up again
#            print 'sql_drop: ', sql_drop
#            print 'sql_create: ', sql_create
#            print 'sql_import:', sql_import
#            print 'result = ', result

            if result == 0:
                #when done, move the TXT file to archive
                to_file = status["mypath"] + '/archive/' + time.strftime('%Y_%m_%d') + \
                    '/' + str(status["myfile"])
                ensure_dir(to_file)
                shutil.move(fullfilename, to_file)
#                shutil.copy(fullfilename, to_file)

    # write summary in a log file and return ID

    except IOError as e:
        status["error"] = "({})".format(e)

    status["duration"] = str(timeit.default_timer() - start_time)
    return status


########################################################################
# MAIN
########################################################################

sapfile_setup = [{"keyword": 'willem', "header_field": 'zzzz', "table_name": 't1'},
    {"keyword": 'willem', "header_field": 'test', "table_name": 'w1'},
    {"keyword": 'willem', "header_field": 'zzz', "table_name": 't2'},
    ]


mypath = 'C:/junk/_sapfiles'            # where to find the TXT files
APP_PATH = 'C:/junk/_test'          # where to find the DB & /temp/ directory

file_list = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for txtfile in file_list:
    file2load = os.path.join(mypath, txtfile)
    status = fileload_sqlite(file2load, sapfile_setup)
    print  status
    sys.stdout.flush()

