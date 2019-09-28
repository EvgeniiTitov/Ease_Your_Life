# Represent DB as a class? methods - different commands! Attributes - its condition, status etc.
# https://www.sqlitetutorial.net/sqlite-cheat-sheet/
# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\results_to_database.py

import sqlite3
import sys

default_path = r"C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\database.db"

def insert_table():
    with connection:
        cursor.execute(generate_SQL_command("INSERT"))

def modify_table():
    pass

def delete_table():
    '''
    Delete a table from the database
    '''
    with connection:
        try:
            cursor.execute(generate_SQL_command("DELETETABLE"))
            print(f"The table has been successfully deleted")
        except:
            print(f"Error! Something went wrong")

def list_tables():
    '''
    Returns list of tables. Confirm a table has been successfully created if it is in the list of tables
    '''
    cursor.execute(generate_SQL_command("LISTTABLES"))
    tables = cursor.fetchall()  # NOTE fetchall() fetches just once! Do it again and you end up with None
    if tables:
        print("Tables:", ', '.join(table[0] for table in tables))
    else:
        print("There are no tables in the database")
    return tables # To see if we've got any tables (important for delete function)

def create_table():
    '''
    Creates table(s)
    '''
    try:
        cursor.execute(generate_SQL_command("CREATETABLE"))
    except sqlite3.OperationalError:
        print(f"Failed to create the table")
        return
    return list_tables()

def read_content():
    try:
        cursor.execute(generate_SQL_command("READCONTENT"))
    except sqlite3.OperationalError:
        print("Failed to show the table")

    names = [column[1] for column in cursor.fetchall()]
    print(names)

def generate_SQL_command(action):
    '''
    Generates SQL commands depending on the action to perform.
    '''
    if action == "CREATETABLE":
        table_name = input("Enter a new table's name: ")
        print("Provide column details. Type DONE to continue")
        columns = []
        counter = 1
        while True:
            user_input = input(f"Column {counter}: ")
            if user_input.upper().strip() == "DONE":
                break
            columns.append(user_input)
            counter += 1
        piece_1 = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        piece_2 = ', '.join(columns)
        return piece_1 + piece_2 + ")"

    if action == "DELETETABLE":
        table_name = input("Enter table to delete: ")
        return f"DROP TABLE {table_name}"

    if action == "LISTTABLES":
        return "SELECT name FROM sqlite_master WHERE type = 'table'"

    if action == "READCONTENT":
        table_name = input("Enter table to show: ")
        return f"PRAGMA TABLE_INFO({table_name})"

    if action == "INSERT":
        table_name = input("Enter table to insert in: ")
        read_content()
        values_to_insert = input("Enter values to insert: ").split()
        return f"INSERT INTO {table_name} VALUES ({', '.join(values_to_insert)})"

def initialize_database(path_to_db=default_path):
    '''
    Establish connection to DB. Specify path to a DB to connect or create a new one.
    '''
    try:
        sql_connection = sqlite3.connect(path_to_db)
    except sqlite3.Error as Error:
        print("Error happened:", Error)
        return

    print("Connection has been established")
    return sql_connection

def main():
    global cursor, connection
    user_input = input("\nCreate or connect to existing DB? CREATE / EXISTING: ")
    # INITIALIZE A DATABASE
    if user_input.upper().strip() == "CREATE":
        connection = initialize_database(input("Specify path to a new DB: "))
    else:
        connection = initialize_database()
    cursor = connection.cursor()
    # INTERACTION WITH A USER:
    while True:
        user_input = input("\nSelect action: CREATETABLE, LISTTABLES, DELETETABLE, INSERT, READ, DELETE, or EXIT: ")

        if user_input.upper().strip() == "CREATETABLE":
            create_table()

        elif user_input.upper().strip() == "LISTTABLES":
            list_tables()

        elif user_input.upper().strip() == "DELETETABLE":
            if list_tables():
                delete_table()
            else:
                print("There are no tables")

        elif user_input.upper().strip() == "INSERT":
            if list_tables():
                insert_table()
            else:
                print("There are no tables. You need to create one first!")

        elif user_input.upper().strip() == "READ":
            if list_tables():
                read_content()
            else:
                print("There are no tables")

        elif user_input.upper().strip() == "DELETE":
            pass

        elif user_input.upper().strip() == "EXIT":
            print("See you!")
            sys.exit()

        else:
            print("Wrong input!")

        if input("\nWould you like to perform another operation? YES/NO: ").upper().strip() == "NO":
            print("See you!")
            connection.close()
            sys.exit()

if __name__ == "__main__":
    main()