"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""

import json
import csv
import os


vessels_list = []


def load_vessels(directory):
    skipped = 0 # Start a counter for skipped vessels at 0

    filenames = os.listdir(directory) # Find the file names in the directory

    print("\nRegistered HarborFlow vessels:")
    
    for file in filenames: # Loop through each name
        path = directory+file 
        if not load_json_vessel(path): # Run load_json_vessel for each file and check if it returned false
            skipped += 1 # If it returned false, report a skipped vessle

    print(f"Skipped vessel files: {skipped}")


def load_json_vessel(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            raw_text = file.read() # Read the json file
            try:
                vessel = json.loads(raw_text) # Convert to dictonary if possible
                vessels_list.append(vessel) # Add new vessel to the list
                print(f"- {vessel["name"]} | IMO {vessel["imo"]} | {vessel["capacity_teu"]} TEU") # Print the vessel details
                return True 

            except json.decoder.JSONDecodeError: # If it can't be converted to a dict, return False to later report skip
                return False

    except FileNotFoundError:
        print(f"Missing file")


# Take the directory of any folder and make a list of dictionaries of every file in it
def get_dictionary_list(directory):
    dictionary_list = []
    
    filenames = os.listdir(directory) # Find the file names

    for name in filenames: # Loop through each file name
            path = directory+name 
            try:
                with open(path, "r", encoding="utf-8") as file:
                    raw_text = file.read() # Read the json file
                    try:
                        dictionary = json.loads(raw_text) # Convert to dictonary if possible
                        dictionary_list.append(dictionary) # Adds all dictionaries to a list
                        
                    except json.decoder.JSONDecodeError: 
                        pass
            
            except FileNotFoundError:
                print("File not found")
                return
            
    return dictionary_list


def open_csv_file(directory):
    try:
        with open(directory, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader) # I CHANGED IT SO IT SKIPS THE HEADER, IF THIS FUCKS UP OTHER FUNCTIONS CHANGE IT BACK <3
            rows = list(reader) # Rows is a list. Each element is a list of columns.
            return rows
    except FileNotFoundError:
        return False


def write_csv_file(directory, rows):
    with open(directory, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def find_vessel(vessel_name):
    found_vessel = False
    selected_vessel_id = 0
    for vessel in vessels_list:
        if vessel_name == vessel["name"].upper(): # If the vessel name is the same as the one inputted by the user:
            selected_vessel_id = vessel["vessel_id"] # This is the ID of the vessel the user wants
            found_vessel = True
            return selected_vessel_id

    if selected_vessel_id == 0: # If the vessel wasn't found, return
        print("Vessel not found")
    
