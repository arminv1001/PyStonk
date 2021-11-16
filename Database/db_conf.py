import sqlite3
from datetime import datetime
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def execusionFirst(conn):
    sql = """Insert into execusion(id,execusionCount,execusionDate) VALUEs(?,?,?)"""
    currentDateTime = datetime.now()
    insertValue = (1,0,currentDateTime)
    cur = conn.cursor()
    cur.execute(sql, insertValue)
    conn.commit()

def main():
    database = "Database/position.db"

    currentOpenPositions = """ CREATE TABLE IF NOT EXISTS OpenPositions (
                                        orderID integer PRIMARY KEY,
                                        tradingSystem varchar(255) not null
                                    ); """

    execusionTable = """CREATE TABLE IF NOT EXISTS execusion (
                                    id integer PRIMARY KEY,
                                    execusionCount integer not null,
                                    execusionDate date not null
                                );"""
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, currentOpenPositions)

        # create tasks table
        create_table(conn, execusionTable)
        # execusion 0
        execusionFirst(conn)

    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()