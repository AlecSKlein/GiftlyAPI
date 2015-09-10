from distutils.log import Log

__author__ = 'Alec'
import sqlite3
import sys
import os
import uuid
import formatting

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
    cursor.execute("CREATE TABLE IF NOT EXISTS Friend(FRIENDID INTEGER PRIMARY KEY, USERID INTEGER REFERENCES User(USERID), NAME TEXT, DOB TEXT, STATE INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Interest(INTERESTNAME TEXT PRIMARY KEY, FRIENDID INTEGER REFERENCES Friend(FRIENDID),  STATE INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Gift(ASIN TEXT PRIMARY KEY, FRIENDID INTEGER REFERENCES Friend(FRIENDID), DESCRIPTION TEXT,  STATE INTEGER)")
    conn.commit()

def execute_insertion_command(sqlcommand):
    try:
        conn = get_connection()
        _init_db(conn)
        cursor = conn.cursor()
        cursor.execute(sqlcommand)
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError, e:
        print "#TODO: LOG"
        if e.message == 'column EMAIL is not unique':
            print "SQL Integrity Error 1: " + e.message
        if e.message == 'column USERID is not unique':
            print "SQL Integrity Error 2: " + e.message
        return False
    return True

def execute_fetch_command(sqlcommand):
    try:
        conn = get_connection()
        _init_db(conn)
        cursor = conn.cursor()
        cursor.execute(sqlcommand)
        conn.commit()
        fetched_values = []
        fetch_all = cursor.fetchall()
        for fetch_one in fetch_all:
            fetched_values.append(fetch_one)
        conn.close()
        if fetched_values:
            return fetched_values
    except sqlite3.IntegrityError, e:
        print "#TODO: LOG"
        if e.message == 'column EMAIL is not unique':
            print "SQL Integrity Error 1: " + e.message
        if e.message == 'column USERID is not unique':
            print "SQL Integrity Error 2: " + e.message
    return None

def insert_column(table, valuenames, values):
    sqlcommand = "INSERT INTO " + table + "(" + ', '.join(valuenames) + ") VALUES(" + ', '.join(values) + ")"
    print sqlcommand
    return execute_insertion_command(sqlcommand)

def insert_user(values):
    table = 'User'
    valuenames = ('USERID', 'EMAIL', 'FNAME', 'LNAME', 'PASSWORD', 'STATE')
    if row_exists('EMAIL', 'User', where=("EMAIL="+str(values[1]))):
        return False
    elif row_exists('USERID', 'User', where=("USERID="+str(values[0]))):
        new_values = (generate_uuid(),) + values[1:]
        insert_user(new_values)
    else:
        insert_column(table, valuenames, values)
    return True

def insert_friend(values):
    table = 'Friend'
    valuenames = ('FRIENDID', 'USERID', 'NAME', 'DOB', 'STATE')
    if not row_exists('USERID', 'User', where=("USERID="+str(values[1]))):
        return False
    elif row_exists('FRIENDID', 'Friend', where=("FRIENDID="+str(values[0]))):
        new_values = (generate_uuid(),) + values[1:]
        insert_friend(new_values)
    else:
        return insert_column(table, valuenames, values)

def insert_interest(values):
    table = 'Interest'
    valuenames = ('INTERESTNAME', 'FRIENDID', 'STATE')
    return insert_column(table, valuenames, values)

def insert_gift(values):
    table = 'Gift'
    valuenames = ('ASIN', 'FRIENDID', 'DESCRIPTION', 'STATE')
    return insert_column(table, valuenames, values)


def get_friendid_by_name_and_dob(userid, name, dob, state=1):
    name = formatting.stringify_sql(name)
    dob = formatting.stringify_sql(dob)
    friendid = select_values("FRIENDID", "FRIEND", where="USERID="+userid+" AND NAME="+name+" AND DOB="+dob, state=state)
    return friendid

def update_table(table, set, where):
    sqlcommand = "UPDATE " + table + " SET " + set + " WHERE " + where
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sqlcommand)
    conn.commit()

def change_row_state(table, state, where):
    update_table(table, "SET STATE="+state, where)

def select_values(values, table, where=None, state='1'):
    sqlcommand = "SELECT " + values + " FROM " + table
    if where:
        sqlcommand += " WHERE " + where
    if state is not None:
        sqlcommand += " AND STATE=" + state
    val = execute_fetch_command(sqlcommand)
    return val

def row_exists(value, table, where, state=1):
    where = where + " AND STATE=" + state
    sqlcommand = "SELECT " + value + " FROM " + table + " WHERE " + where
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sqlcommand)
    conn.commit()
    result = cursor.fetchall()
    if result:
        return True
    return False

def row_to_dict(rows):
    d ={} # the dictionary to be filled with the row data and to be returned

    for i, row in enumerate(rows): # iterate throw the sqlite3.Row objects
        l = [] # for each Row use a separate list
        for col in range(0, len(row)): # copy over the row date (ie. column data) to a list
            l.append(row[col])
        d[i] = l # add the list to the dictionary
    return d

def generate_uuid():
    id = str(uuid.uuid4().int)[0:12]
    return id