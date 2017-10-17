import timeit
import os
import string
import time
import shutil
from os import listdir
from os.path import isfile, join, getsize, getctime
import sys


def ensure_dir(f):
    """
    http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
    """
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

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
                        status["header_fields"] = splitline
                        status["header_fields_count"] = len(splitline)
#                        field_tuple, value_tuple = get_fields(splitline)
#                field_len = len(field_tuple)
#       s = "\t".join(str(x).strip(' \t\n') for x in field_tuple) + '\n'

                    elif linenum > MAX_SEARCH:
                        break

        input.close()
        status["linenum_end"] = linenum

        # create SQL and TXT file

        # move the file to archive
        to_dir = status["mypath"] + '/archive/' + time.strftime('%Y_%m_%d') + '/'
        ensure_dir(to_dir)
        shutil.move(fullfilename, to_dir + '/' + str(status["myfile"]))
    #    shutil.copy(fullfilename, to_dir + '/' + str(status["myfile"]))

    # write summary in a log file and return ID

    except IOError as e:
        print("({})".format(e))

    status["duration"] = str(timeit.default_timer() - start_time)
    return status


########################################################################
# MAIN
########################################################################

sapfile_setup = [{"keyword": 'willem', "header_field": 'zzzz', "table_name": 'willem_zzzz'},
    {"keyword": 'willem', "header_field": 'field', "table_name": 'willem_field'},
    {"keyword": 'willem', "header_field": 'zzz', "table_name": 'willem_zzz'},
    ]

mypath = 'C:\junk\_test'
file_list = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for txtfile in file_list:
    status = fileload_sqlite( mypath + '/' + txtfile, sapfile_setup)
    print  status
    sys.stdout.flush()

