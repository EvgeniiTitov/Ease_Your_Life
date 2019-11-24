from collections import defaultdict
import os
import sys


class FilesManager:

    def search_file(self, filename, search_locations = ("C:", "D:")):
        """
        Searches for the filename provided. By default checks all computer. Optimize search, too slow.
        :param filename:
        :param search_locations:
        :return:
        """
        potential_findings = list()

        for directory in search_locations:
            for dir_path, dir_names, file_names in os.walk(directory):
                for file_name in file_names:
                    if filename in file_name.lower():
                        potential_findings.append((file_name, os.path.join(dir_path, file_name)))
                for dir in dir_names:
                    if filename in dir.lower():
                        potential_findings.append((dir, os.path.join(dir_path, dir)))

        return potential_findings

    def delete_file(self):
        pass

    def explore_content(self, path_to_explore, files_found):
        """
        Recursively (os.walk()) explores folder's content
        :param path_to_explore: path to explore
        :param files_found: stores files found. Defaultdict!
        :return:
        """
        assert type(files_found) == dict

        for filename in os.listdir(path_to_explore):
            path_filename = os.path.join(path_to_explore, filename)
            if os.path.isfile(path_filename):
                files_found[os.path.splitext(path_filename)[-1].lower()].append(filename)
            else:
                files_found["folder"].append(filename)
                self.explore_content(path_filename, files_found)

        return files_found

    def relocate_content(self, to_relocate, destination):
        """
        Relocates file(s) to a new user provided place
        :param to_relocate: file or a folder
        :param destination: new place to store file(s)
        :return:
        """
        if not os.path.isfile(to_relocate):

            if len(os.listdir(to_relocate)) == 0:
                print("Empty folder. Nothing to move")
                return

            for filename in os.listdir(to_relocate):
                filename_path = os.path.join(to_relocate, filename)
                os.rename(filename_path, os.path.join(destination, filename))
        else:
            os.rename(to_relocate, os.path.join(destination, os.path.split(to_relocate)[-1]))

        return 1

class ManagerWrapper:

    def __init__(self):
        self.files_manager = FilesManager()

    def search(self):
        file_to_find = input("Enter file's name: ")
        potential_location = input("Potential location or NO in case you don't know: ")

        print("Searching...")
        if not potential_location.upper().strip() == "NO":
            findings = self.files_manager.search_file(file_to_find.lower(),
                                                      search_locations=list(potential_location))
        else:
            findings = self.files_manager.search_file(file_to_find.lower())

        if findings:
            print("\nFollowing files found:")
            for filename, path_to_file in findings:
                print("Found:", filename, " here:", path_to_file)
        else:
            print("\nNo files have been found")

    def delete(self):
        to_delete = input("Provide file's name or path to the file")
        # Check if it is a path?



    def relocate(self):
        to_relocate = input("Path to the file to relocate: ")
        destination = input("Destination: ")

        if not os.path.exists(destination):
            os.mkdir(destination)

        success = self.files_manager.relocate_content(to_relocate, destination)
        if success:
            print("Relocation complete")

    def explore(self):
        location_to_explore = input("Location to explore: ")

        if not os.path.isdir(location_to_explore):
            print("ERROR: Explore only works for folders!")
            return

        to_store_files = defaultdict(list)
        files_explored = self.files_manager.explore_content(location_to_explore, to_store_files)

        print("\nThe following files have been found:")
        total_files = 0
        for extension, files in files_explored.items():
            print(f"Ext: {extension}, nb of files: {len(files)}")
            total_files += len(files)
        print("TOTAL NUMBER:", total_files)


def main():

    manager = ManagerWrapper()

    while True:
        action = input("Select action SEARCH / DELETE / RELOCATE / EXPLORE / EXIT: ")
        if action.upper().strip() == "EXIT":
            print("Exiting")
            sys.exit()
        elif action.upper().strip() == "SEARCH":
            manager.search()
        elif action.upper().strip() == "DELETE":
            manager.delete()
        elif action.upper().strip() == "RELOCATE":
            manager.relocate()
        elif action.upper().strip() == "EXPLORE":
            manager.explore()

        next_action = input("\nWould you like to perform another operation? Y / N: ")
        if next_action.upper().strip() == "N":
            print("See you!")
            break

if __name__ == "__main__":
    main()
