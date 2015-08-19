from distutils.log import Log

__author__ = 'Alec'
import sqlite3
import sys
import os
import json
import uuid

def _connect_db():
    conn = None
    try:
        conn = sqlite3.connect(os.getcwd() + '/databases/giftly.db')
        #This line causes returned lists to instead be Key-Value pairs of Column-Value
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
    cursor.execute("CREATE TABLE IF NOT EXISTS User(USERID INTEGER UNIQUE, EMAIL TEXT PRIMARY KEY, FNAME TEXT, LNAME TEXT, PASSWORD TEXT, STATE INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Friend(FRIENDID INTEGER PRIMARY KEY, EMAIL TEXT REFERENCES User(EMAIL), NAME TEXT, STATE INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Interest(INTERESTNAME TEXT PRIMARY KEY, FRIENDID INTEGER REFERENCES Friend(FRIENDID),  STATE INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Gift(ASIN TEXT PRIMARY KEY, FRIENDID INTEGER REFERENCES Friend(FRIENDID), DESCRIPTION TEXT,  STATE INTEGER)")
    conn.commit()

def _insert_samples():
    conn = _connect_db()
    _init_db(conn)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO User(USERID, EMAIL, FNAME, LNAME, PASSWORD, STATE) VALUES(1, 'Alec@gmail.com', 'Alec', 'Klein', 'MyPassword', 1)")
    cursor.execute("INSERT INTO Friend(FRIENDID, EMAIL, NAME, STATE) VALUES(2, 1, 'Justin', 1)")
    cursor.execute("INSERT INTO Friend(FRIENDID, EMAIL, NAME, STATE) VALUES(3, 1, 'Mike', 1)")
    cursor.execute("INSERT INTO Friend(FRIENDID, EMAIL, NAME, STATE) VALUES(4, 1, 'Tom', 1)")
    conn.commit()
    conn.close()

def execute_command(sqlcommand):
    try:
        conn = _connect_db()
        _init_db(conn)
        cursor = conn.cursor()
        cursor.execute(sqlcommand)
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError, e:
        print "#TODO: LOG"
        print "SQL Integrity Error: " + e.message
        return False
    return True

def insert_column(table, valuenames, values):
    sqlcommand = "INSERT INTO " + table + "(" + ', '.join(valuenames) + ") VALUES(" + ', '.join(values) + ")"
    print sqlcommand
    return execute_command(sqlcommand)

def insert_user(values):
    table = 'User'
    valuenames = ('USERID', 'EMAIL', 'FNAME', 'LNAME', 'PASSWORD', 'STATE')
    if not insert_column(table, valuenames, values):
        print "Error caught"
        new_values = (generate_uuid(),) + values[1:]
        insert_user(new_values)

def select_values(values, table, where=None):
    sqlcommand = "SELECT " + values + " FROM " + table
    if where:
        sqlcommand += " WHERE " + where
    execute_command(sqlcommand)

def generate_uuid():
    id = str(uuid.uuid4().int)[0:12]
    return id