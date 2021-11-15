import os
import sqlite3
from datetime import datetime
from sqlite3 import Error

def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    :return: Connection object or None
    """
    dirname = os.path.dirname(__file__)
    database = os.path.join(dirname, 'position.db')
    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)
    return conn

def insertOrderID(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """
    sql = ''' INSERT INTO OpenPositions(orderID,tradingSystem)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

def saveOrderID(orderID,tradingSystem):
    conn = create_connection()
    task = (orderID,tradingSystem)
    insertOrderID(conn,task)
    conn.close()

def deleteOrderID(orderID):
    conn = create_connection()
    sql = 'DELETE FROM OpenPositions WHERE orderID=?'
    cur = conn.cursor()
    cur.execute(sql,(orderID,))
    conn.commit()
    conn.close()

def updateExecusion(execusion):
    conn = create_connection()
    sql = ''' UPDATE execusion SET execusionCount = ? ,execusionDate = ? WHERE id = ?'''
    cur = conn.cursor()
    task = (execusion,datetime.now(),1)
    cur.execute(sql, task)
    conn.commit()
    conn.close()

def readExecusion():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM execusion")
    rows = cur.fetchall()
    return (rows[0][1])

def readOrderID(tradingSystem):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM OpenPositions where tradingSystem == ?",(tradingSystem,))
    rows = cur.fetchall()
    if len(rows) > 0:
        return (rows[0][0])
    else:
        return 0

def tests():
    saveOrderID(1,"test")
    orderId = readOrderID("test")
    print(readExecusion())
    deleteOrderID(orderId)
    print(readOrderID("test"))

if __name__ == "__main__":
    tests()