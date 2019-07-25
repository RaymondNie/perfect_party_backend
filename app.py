#!flask/bin/python3
from flask import Flask
from flask import request
from flask_cors import CORS

import psycopg2
from psycopg2 import sql

import json
import datetime

app = Flask(__name__)
CORS(app)

def datetimeconv(dt):
    if isinstance(dt, datetime.datetime):
        return dt.__str__()

# Setup database connection
try:
    connection = psycopg2.connect(
        user='rnie',
        password='doghot123',
        host='127.0.0.1',
        database='perfect_party'
    )
    cursor = connection.cursor()
    print("Successfully connected to Database")
    print(connection.get_dsn_parameters(), "\n")

except (Exception, psycopg2.Error) as error:
    print("Error while connection to PostgreSQL", error)

# Basic get requests
@app.route('/get_table', methods=['GET'])
def get_table():
    table_name = request.args.get('tablename')
    query = 'select * from {}'.format(table_name)
    try: 
        cursor.execute(query)
    except:
        cursor.execute("ROLLBACK")
        connection.commit()
    # Create a dictionary from the query results and return it as a json object
    r = [dict((cursor.description[i][0], str(value)) for i, value in enumerate(row)) \
            for row in cursor.fetchall()]
    return json.dumps(r, default = datetimeconv)

# Advanced get request
@app.route('/get_venue', methods=['GET'])
def get_venue():
    table_name = 'venue'
    capmin = request.args.get('capmin')
    capmax = request.args.get('capmax')
    pricemin = request.args.get('pricemin')
    pricemax = request.args.get('pricemax')

    query = 'select * from {} where venuecapacity > {} and venuecapacity < {} and rentalprice > {} and rentalprice < {}'.format(table_name, capmin, capmax, pricemin, pricemax)
    try: 
        cursor.execute(query)
    except:
        cursor.execute("ROLLBACK")
        connection.commit()
    # Create a dictionary from the query results and return it as a json object
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) \
            for row in cursor.fetchall()]
    return json.dumps(r, default = datetimeconv)

# Advanced get request
@app.route('/get_review', methods=['GET'])
def get_review():
    table_name = 'review'
    rating = request.args.get('rating')
    userid = request.args.get('userid')
    itemid = request.args.get('itemid')

    query = 'select * from {} where rating = {}'.format(table_name, rating)
    if userid != '':
        query += " and userid = {}".format(userid)
    if itemid != '':
        query += " and itemid = {}".format(itemid)

    try: 
        cursor.execute(query)
    except:
        cursor.execute("ROLLBACK")
        connection.commit()
    # Create a dictionary from the query results and return it as a json object
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) \
            for row in cursor.fetchall()]
    return json.dumps(r, default = datetimeconv)

# Delete row
@app.route('/delete_row', methods=['POST'])
def delete_row():
    tablename = request.args.get('tablename')
    colname = request.args.get('colname')
    rowid = request.args.get('rowid')
    query = "delete from {} where {} = {}".format(tablename, colname, rowid)
    try: 
        cursor.execute(query)
        connection.commit()
    except:
        
        cursor.execute("ROLLBACK")
        connection.commit()
        return 3
    return '<p>Successful delete</p>'

# Update row
@app.route('/update_row', methods=['POST'])
def update_row():
    tablename = request.args.get('tablename')
    columns = request.args.get('columns')
    values = request.args.get('values')
    prikey = request.args.get('prikey')
    pkvalue = request.args.get('pkvalue')

    columns = columns.split(",")
    values = values.split(",")

    query = "update {} set ".format(tablename)
    if type(columns) == list:
        for i in range(len(columns)):
            query += "{} = {},".format(columns[i], values[i])
        query = query[:-1] # removing last comma
    else:
        query += "{} = {}".format(columns, values)
    query += " where {} = {}".format(prikey, pkvalue)

    try: 
        print(query)
        cursor.execute(query)
        connection.commit()
    except:
        cursor.execute("ROLLBACK")
        connection.commit()
        return '<p>Row update failed</p>'
    return '<p>Row updated</p>'

# Post request to create new users
@app.route('/insert_row', methods=['POST'])
def insert_row():
    tablename = request.args.get('tablename')
    columns = request.args.get('columns')
    values = request.args.get('values')
    query = "insert into {} (".format(tablename) + columns + ") values (" + values + ")"
    try: 
        print(query)
        cursor.execute(query)
        connection.commit()
    except:
        cursor.execute("ROLLBACK")
        connection.commit()
        return '<p>Row insert failed</p>'
    return '<p>Row inserted</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
