"""File loading and path-handling functions for HarborFlow.

Create reusable JSON and CSV loaders here. Do not hard-code sample records.
"""

import json
import csv
import os
import datetime


vessels_list = []

def load_vessels(directory):
    skipped = 0 # Start a counter for skipped vessels at 0

    filenames = os.listdir(directory) # Find the file names in the directory

    print("\nRegistered HarborFlow vessels:")
    
    for file in filenames: # Loop through each name
        path = directory+file 
        if not load_json_vessel(path): # Run load_json_vessle for each file and check if it returned false
            skipped += 1 # If it returned false, report a skipped vessle

    print(f"Skipped vessel files: {skipped}")


def load_json_vessel(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            raw_text = file.read() # Read the json file
            try:
                vessel = json.loads(raw_text) # Convert to dictonary if possible
                vessels_list.append(vessel)
                print(f"- {vessel["name"]} | IMO {vessel["imo"]} | {vessel["capacity_teu"]} TEU") # Print the vessel details
                return True 

            except json.decoder.JSONDecodeError: # If not, return False to later report skip
                return False

    except FileNotFoundError:
        print(f"Missing file")


def get_vessel_list(directory):
    
    filenames = os.listdir(directory) # Find the file names

    for file in filenames: # Loop through each file name
            path = directory+file 
            try:
                with open(path, "r", encoding="utf-8") as vessel_file:
                    raw_text = vessel_file.read() # Read the json file
                    try:
                        vessel = json.loads(raw_text) # Convert to dictonary if possible
                        vessels_list.append(vessel) # Adds all vessel dictionaries to a list
                        
                    except json.decoder.JSONDecodeError: 
                        pass
            
            except FileNotFoundError:
                print("Vessel not found")
                return
    return vessels_list


