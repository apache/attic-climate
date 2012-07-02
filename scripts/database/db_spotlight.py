'''This is a small collection of Bottle web services
that merely expose the wrm_prod database parameters
table in the form of HTML tables.

Each endpoint will return a fully formed HTML table,
(well at least that is the plan)'''

from bottle import run, route
import pymysql
import datetime
import sys

def db_connect():
    conn = pymysql.connect(host='localhost', port=3306, user='wrm_data', passwd='wrm_data', db='wrm_prod')
    cur = conn.cursor()
    cur.execute("select d.dataset_id , p.* from dataset d, parameter p where d.dataset_id = p.dataset_id;")
    #cur.execute("SELECT * FROM parameter")
    return cur, conn

def columns(cur):
    # Build list of column names
    column_list = [x[0] for x in cur.description]
    return column_list

def get_th_row(cur):
    # Build list of column names
    column_list = columns(cur)
    # Define static HTML elements for the THEAD
    thead_start = ['<thead>\n\t<tr>\n']
    thead_end = '\t</tr>\n</thead>'
    # Append all column names to the HTML starting block
    for column in column_list:
        th_element = '\t\t<th>%s</th>\n' % column
        thead_start.append(th_element)
    # Add on the closing THEAD tag
    thead_start.append(thead_end)
    # Convert the List into a string and return
    return ''.join(thead_start)

def get_tbody(cur):
    # Setup the initial tbody HTML
    tbody = ['\t<tbody>\n']
    # Fetch the entire table from the db
    row_tup = cur.fetchall()
    # Loop over the returned results and do some datetime conversion cleanup
    # and append the formal HTML to the tbody list
    for row in row_tup:
        tbody.append('\t\t<tr>\n')
        for val in row:
            # Check on datetime.date fields and convert
            if isinstance(val, datetime.date):
                val = val.strftime('%Y-%m-%d')
            # Convert None values into '-' instead
            elif val== None:
                val = '-'
            # Wrap the val in HTML and append to tbody
            element = '\t\t\t<td>%s</td>\n' % val
            tbody.append(element) 
        #Close out the HTML
        tbody.append('\t\t</tr>\n')
    tbody.append('\t</tbody>\n')
    # Join the list into a string and return
    return ''.join(tbody)

def param_html(cur):
    # Setup the static Table HTML
    table = ['<table>\n','</table>\n']
    # Grab the HEAD & BODY content
    head = get_th_row(cur)
    body = get_tbody(cur)
    # Add the content to the Table List
    table.insert(1, head)
    table.insert(2, body)
    # Convert the list into a string and return
    table_out = ''.join(table)
    return table_out

def cleanse_row(row):
    # Empty list to collect all cleaned up elements
    row_list = []
    for val in row:
        if isinstance(val, datetime.date):
            val = val.strftime('%Y-%m-%d')
        row_list.append(val)
    return row_list
   


def param_json(cur):
    object_list = {"param":[]}
    #json_param = {"rows":[]}
    keys = columns(cur)
    data_tuple = cur.fetchall()
    for row in data_tuple:
        row_list = cleanse_row(row)
        print row_list
        object_list['param'].append(dict(zip(keys, row_list)))

    print object_list

    return object_list

def close_db(cur, conn):
    cur.close()
    conn.close()





@route('/rcmed/param.:format')
@route('/rcmed/param.:format/')
def get_param(format):
    # Connect to the database
    cur, conn = db_connect()
    if format == 'html':
        #response = param_html(cur)
        response = { "Key": 5 }
    elif format == 'json':
        response = param_json(cur)
    else:
        response = '<p> Bad request.  You should pass in /rcmed/param/[json] or [html]</p>'
    close_db(cur, conn)
    return response


run(host='argo.jpl.nasa.gov', port=8886)
