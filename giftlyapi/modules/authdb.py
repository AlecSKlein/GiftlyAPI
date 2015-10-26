__author__ = 'Alec'

import sqlite3
import sys
import os
import uuid
from datetime import datetime
import formatting

def _connect_db():
    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + '/databases/auth.db')
        # This line causes returned lists to instead be Key-Value pairs of Column-Value
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT SQLITE_VERSION()')
        print "SQLite version: %s" % cursor.fetchone()

    except sqlite3.Error, e:
        print "Error %s: " % e.args[0]
        sys.exit(1)

    return conn

def get_connection():
    return _connect_db()

def _init_db(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Auth(EMAIL TEXT PRIMARY KEY, APIKEY TEXT UNIQUE, DATECREATED DATE)")
    conn.commit()

def insert_default():
    sqlcommand = "INSERT INTO Auth('EMAIL', 'APIKEY', 'DATECREATED') VALUES('Me2@email.com', 'apikey2', CURRENT_TIMESTAMP)"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sqlcommand)
    conn.commit()
    conn.close()

def execute_insertion(table, valuenames, values):
    sqlcommand = "INSERT INTO " + table + "(" + ', '.join(valuenames) + ") VALUES(" + ', '.join(values) + ")"
    try:
        conn = get_connection()
        _init_db(conn)
        cursor = conn.cursor()
        cursor.execute(sqlcommand)
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError, e:
        print "Error" + e.message

def insert_auth(values):
    table = 'Auth'
    valuenames = ('EMAIL', 'APIKEY', 'DATECREATED')
    execute_insertion(table, valuenames, values)

def authenticate(email, api_key):
    email = formatting.stringify_sql(email)
    api_key = formatting.stringify_sql(api_key)
    sqlcommand = "SELECT EMAIL,APIKEY FROM Auth WHERE EMAIL=" + email + " AND APIKEY=" + api_key
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sqlcommand)
    conn.commit()
    result = cursor.fetchall()
    if result:
        return True
    return False

def generate_api_key():
    id = str(uuid.uuid4())
    id = id[0:13]+id[-13:-1]
    print id
    return id

def generate_current_timestamp():
    current_timestamp = datetime.today().strftime('%Y-%m-%d')
    return current_timestamp
