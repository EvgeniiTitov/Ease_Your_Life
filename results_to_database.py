# Represent DB as a class? methods - different commands! Attributes - its condition, status etc.

# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\results_to_database.py

import sqlite3
import sys

default_path = r"C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\database.db"

def insert_table():
    pass

def modify_table():
    pass

def delete_table(name):
    '''
    Delete a table from the database
    '''
    with connection:
        try:
            cursor.execute(f"""DROP TABLE {name}""")
            print(f"The table {name} has been successfully deleted")
        except:
            print(f"Error! The table {name} doesn't exist")

def confirm_tables():
    '''
    Returns list of tables. Confirm a table has been successfully created if it is in the list of tables
    '''
    cursor.execute(generate_SQL_command("LIST_TABLES"))
    tables = cursor.fetchall()  # NOTE fetchall() fetches just once! Do it again and you end up with None
    if tables:
        print("Tables:", ', '.join(table[0] for table in tables))
    else:
        print("There are no tables in the database")
    return tables # To see if we've got any tables (important for delete function)

def create_table(*args):
    '''
    Creates table(s)
    '''
    for table in args:
        try:
            cursor.execute(table)
        except sqlite3.OperationalError:
            print(f"Failed to create the table {table}")
            return

    return confirm_tables()

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

    if action == "LIST_TABLES":
        return "SELECT name FROM sqlite_master WHERE type = 'table'"

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

    if user_input.upper().strip() == "CREATE":
        connection = initialize_database(input("Specify path to a new DB: "))
    else:
        connection = initialize_database()
    cursor = connection.cursor()

    while True:
        user_input = input("\nSelect action: CREATETABLE, LISTTABLES, DELETETABLE, INSERT, READ, DELETE, or EXIT: ")

        if user_input.upper().strip() == "CREATETABLE":
            create_table(generate_SQL_command("CREATETABLE"))

        elif user_input.upper().strip() == "LISTTABLES":
            confirm_tables()

        elif user_input.upper().strip() == "DELETETABLE":
            if confirm_tables():
                delete_table(input("Select table to delete: "))

        elif user_input.upper().strip() == "INSERT":
            pass

        elif user_input.upper().strip() == "READ":
            pass

        elif user_input.upper().strip() == "DELETE":
            pass

        elif user_input.upper().strip() == "EXIT":
            print("See you!")
            sys.exit()

        else:
            print("Wrong input!")

        if input("\nWould you like to perform another operations? YES/NO: ").upper().strip() == "NO":
            print("See you!")
            sys.exit()

if __name__ == "__main__":
    main()