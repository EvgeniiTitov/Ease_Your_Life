"""
Managing directories.

Problems - Bags:
- Fix if '.' in filename:
- Delete wont work for folders. And you need to be careful with recursive deletion method

Improvements
Crucial:
+ explore should tell total number of files found. Them for each extension.
+ allow operations on multiple files (like moving from one directory to another one)
+ when deleting elements add option not to delete anything, changed mind (when you are given indexes and files)
+ search function needs to be in every function so user don't need to provide full paths rather can select of whats offered. For example,
when i want to relocate something, ask for files name, find it and move


Long-term:
+ Include argparse functionality to use console commands.
+ Using trees we could draw folders contents for explore method
+ Introduce custom Error (raise CustomError) to better understand where user fucked up

+ Introduce some functions for data science and NN such as resizing images, making them GrayScale, normalizing, changing extension of images
 (not only to jpg, add different options) etc.
"""
from collections import defaultdict
import os

# SEARCH
def search_file(filename, path = ('C:', 'D:')):
    '''
    :param filename: Name of the file we are looking for
    :return (filename, path to the file) tuples
    '''
    found_files = [] #Should be changed to dict, so that we can return files and folders telling what is what
    for dir in path:
        for dir_path, dir_names, file_names in os.walk(dir):
            #dir_path - path to every directory we enter
            #dir_names - names of all directories in there
            #file_names - names of all files in there
            for file in file_names:
                if filename in file:
                    found_files.append((file, os.path.join(dir_path,file)))
            for directory in dir_names:
                if filename in directory:
                    found_files.append((directory, os.path.join(dir_path, directory)))

    return found_files

def initialize_search():
    '''
    TBA
    '''
    to_find = input("Enter name of the file that you are searching for: ")
    location = input("Do you know the directory in which to search? YES / NO: ")

    if location.upper().strip() == "YES":
        directory = input("Enter the directory: ")
        print('Calling the searching function... Please wait.')
        result = search_file(to_find, directory)
    elif location.upper().strip() == "NO":
        print('Calling the searching function... Please wait.')
        result = search_file(to_find)
    else:
        print("Wrong input! Try again")
        return

    if result:
        print('\nResults:')
        for finding in result:  #In case more than one file found. Same names.
            print(f'Found < {finding[0]} > at the path < {finding[1]} >')
    else:
        print('No file with this name has been found. Try again.')



# DELETE
def delete_file(path):
    '''
    return: 1 to confirm successful deletion
    '''
    if not os.path.exists(path):
        print("Can't delete file that doesn't exist!")
        return

    try:
        os.remove(path)
        print("File's been deleted!")
    except:
        print('Failed to delete the file')
        return

    return 1

def initialize_delete():
    '''
    TBA
    '''
    print("In order to delete file from the system please provide either the full path to the file or its name")
    interaction_1 = input("Do you know full path to the file? YES / NO: ")

    if interaction_1.upper().strip() == 'NO':
        file_name = input("Enter name of the file to be searched and deleted: ")
        print("\nCalling searching function... Please wait")

        search_result = search_file(file_name)  # Returns tuples (img_name,path)

        if search_result:
            print('The following files have been found:')
            for i,result in enumerate(search_result):
                print(i,result)
            index_to_delete = int(input("Enter index of the file to be deleted: "))
            delete_file(search_result[index_to_delete][1]) #[1] to send path of the file to delete (filename, filepath)
        else:
            print(f'No elements with the name <{file_name}> have been found. Try again!')
    else:
        path = input("Enter path to the file to be deleted: ")
        delete_file(path)



# RELOCATE / RENAME
def relocate_file(file_name, new_NamePath):
    if os.path.exists(file_name):
        try:
            os.rename(file_name, new_NamePath)
            print("File's been relocated. Check at the new path")
        except:
            print('Failed to rename file. Try again')
    else:
        print("The file provided doesn't exist")

    return 1 #relocated successfully

def initialize_relocate():
    '''
    Ask for name of the file to rename. Find the
    '''
    to_relocate = input("Provide path to the file to relocate: ")
    new_path = input("Provide new path to where drop the file: ")
    if os.path.exists(to_relocate):
        relocate_file(to_relocate, new_path)
    else:
        print("Cannot relocate nonexisting file. Try again!")



# EXPLORE
def explore_content(path, files_found):
    """
    Recursively explores content of the folder provided by a user. Collects extensions and files found.
    Can be improved: os.path.isdir('name') vs os.path.isfile('name')
    Return: (ext, nb_of_files).
    """
    try: #some files are broken, to skip them. Tries open them recursively.
        if not os.listdir(path): #Base case: empty directory.
            return files_found   #can be just return. Dictionary didn't get updated in any way anyway.

        for filename in os.listdir(path):
            new_path = os.path.join(path, filename)
            if '.' in filename: #File found. FIX THIS.
                files_found[os.path.splitext(new_path)[-1].lower()].append(filename)
            else:
                files_found['folder'].append(filename) #Folder found
                explore_content(new_path, files_found) #No return here. Once it got back FOR will continue searching.
    except:
        pass

    return files_found #In case there were only files in the folder searched. All have been processed, return
                       #updated dictionary to previous call

def initialize_explore():
    files_found = defaultdict(list)
    directory = input("Enter path to a directory you'd like to explore: ")
    results = explore_content(directory, files_found)

    print("\nThe following files have been found: ")
    for key, value in results.items():
        print(f'Extension: {key}, number of files: {len(results[key])}')



def main():
    print("WELCOME TO THE FILE MANAGEMENT SCRIPT\n")
    status = True
    while status:
        user_input = input("What would you like to do? EXPLORE / SEARCH / DELETE / RELOCATE: ")
        if user_input.upper().strip() == 'EXPLORE':
            initialize_explore()
        elif user_input.upper().strip() == 'SEARCH':
            initialize_search()
        elif user_input.upper().strip() == 'DELETE':
            initialize_delete()
        elif user_input.upper().strip() == 'RELOCATE':
            initialize_relocate()
        else:
            print("Incorrect input. Please try again.")

        user_in = input('\nWould you like to perform another operation? YES / NO: ')
        if user_in.upper().strip() == 'NO':
            print('Thank you. See you!')
            status = False

if __name__ == '__main__':
    main()