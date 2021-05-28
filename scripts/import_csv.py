import csv
from db_functions import *

CLIENT_FILE = "files/Client_14-JAN-2019.csv"
COUNTRY_FILE = "files/Country_14-JAN-2019.csv"


def main():
    database = "TestDB.db"

    conn = create_connection(database)
    with conn:

        delete_values(conn, "CLIENTS")
        delete_values(conn, "COUNTRY")

        with open(CLIENT_FILE) as file:
            import_data = [tuple(line) for line in csv.reader(file)]
            for value in import_data:
                value_id = import_csv(conn, "CLIENTS", value)

        with open(COUNTRY_FILE) as file:
            import_data = [tuple(line) for line in csv.reader(file)]
            for value in import_data:
                value_id = import_csv(conn, "COUNTRY", value)

        print("Grabbing all clients in Brazil")
        query_db(conn, "SELECT * FROM CLIENTS WHERE Country_ID = '4'")

        print("Grabbing all countries")
        query_db(conn, "SELECT * FROM COUNTRY")


if __name__ == '__main__':
    main()
