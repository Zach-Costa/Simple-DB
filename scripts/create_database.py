from db_functions import *


def main():
    database = 'TestDB.db'

    clients_table_name = "CLIENTS"
    clients_table = {"First_Name": "text", "Last_Name": "text", "Country_ID": "integer", "Invoice_Date": "text"}
    clients_query = create_table_query(clients_table_name, clients_table)

    country_table_name = "COUNTRY"
    country_table = {"Country_ID": "integer", "Country_Name": "text"}
    country_query = create_table_query(country_table_name, country_table)

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, clients_query)
        create_table(conn, country_query)
    else:
        print("Error! Can't connect to the database.")

    # sql_create_clients = """CREATE TABLE IF NOT EXISTS CLIENTS (
    #                             id integer PRIMARY KEY,
    #                             [Client_Name] text,
    #                             [Country_ID] integer,
    #                             [Date] text
    #                         )"""
    # sql_create_country = """CREATE TABLE IF NOT EXISTS COUNTRY (
    #                             id integer PRIMARY KEY,
    #                             [Country_ID] integer,
    #                             [Country_Name] text
    #                         )"""
    # conn = create_connection(database)
    #
    # if conn is not None:
    #     create_table(conn, sql_create_clients)
    #     create_table(conn, sql_create_country)
    # else:
    #     print("Error! Cannot connect to the database!")


if __name__ == '__main__':
    main()
