import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_table_query(table_name, key_dict):
    sql_query = "CREATE TABLE IF NOT EXISTS " + table_name + " (\nid integer PRIMARY KEY"
    for key in key_dict:
        sql_query += ",\n[" + key + "] " + key_dict[key]
    sql_query += "\n)"
    print(sql_query)
    return sql_query


def create_table(conn, create_query):
    try:
        c = conn.cursor()
        c.execute(create_query)
    except Error as e:
        print(e)


def import_csv(conn, table, values):
    sql_query = None
    if table == "CLIENTS":
        sql_query = """ INSERT INTO CLIENTS(First_Name,Last_Name,Country_ID,Invoice_Date)
                        VALUES(?,?,?,?) """
    elif table == "COUNTRY":
        sql_query = """ INSERT INTO COUNTRY(Country_ID,Country_Name)
                            VALUES(?,?) """

    c = conn.cursor()
    c.execute(sql_query, values)
    conn.commit()

    return c.lastrowid


def add_entry(conn, values):
    try:
        sql_query = """ INSERT INTO CLIENTS(First_Name,Last_Name,Country_ID,Invoice_Date)
                        VALUES(?,?,?,?) """

        c = conn.cursor()
        c.execute(sql_query, values)
        conn.commit()

        return c.lastrowid
    except Error as e:
        return e


def update_value(conn, values):
    sql_query = """ UPDATE CLIENTS
                    SET First_Name = ?,
                        Last_Name = ?,
                        Country_ID = ?,
                        Invoice_Date = ?
                    WHERE id = ? """

    c = conn.cursor()
    c.execute(sql_query, values)
    conn.commit()

    return values[-1]


def delete_values(conn, table, id=None):
    sql_query = "DELETE FROM " + table
    if id is not None:
        sql_query += " WHERE id = " + str(id)

    print(sql_query)

    c = conn.cursor()
    c.execute(sql_query)
    conn.commit()


def query_db(conn, query):
    c = conn.cursor()
    c.execute(query)

    rows = c.fetchall()

    return rows
