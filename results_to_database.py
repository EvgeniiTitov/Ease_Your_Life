# python C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\results_to_database.py
# Bugs. When READ doesnt show tables even though it exists
import sqlite3
import sys

default_path = r"C:\Users\Evgenii\Desktop\Python_Programming\Python_Projects\Scripts\database.db"


def insert_database():
    pass

def modify_database():
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
    Returns list of tables. Confirm a table has been successfully created
    '''
    cursor.execute("""  SELECT name
                        FROM sqlite_master
                        WHERE type = 'table' """)
    if cursor.fetchall():
        print("List of tables:")
        print(cursor.fetchall())
        print(' '.join(table[0] for table in cursor.fetchall()))
    else:
        print("There are no tables in the database")

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
        user_input = input("\nSelect: CREATE, INSERT, READ, MODIFY, DELETE or EXIT: ")

        if user_input.upper().strip() == "CREATE":
            command = """   CREATE TABLE IF NOT EXISTS {table_name} (
                            name TEXT NOT NULL,
                            salary INTEGER NOT NULL)""".format(table_name=input("Specify table's name: "))
            create_table(command)

        elif user_input.upper().strip() == "INSERT":
            pass

        elif user_input.upper().strip() == "READ":
            confirm_tables()

        elif user_input.upper().strip() == "MODIFY":
            pass

        elif user_input.upper().strip() == "DELETE":
            confirm_tables()
            to_delete = input("Select table to delete: ")
            delete_table(to_delete)

        else:
            print("Wrong input!")

        if input("\nWould you like to perform another operations? YES/NO: ").upper().strip() == "NO":
            print("See you!")
            sys.exit()

if __name__ == "__main__":
    main()