"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import json
import csv
import os
import datetime

from data_access import load_vessels, get_vessel_list

vessels_list = []

def inspect_vessel(vessel_name, reference_date):
    # FIND VESSEL ID
    selected_vessel_id = 0
    
    vessels_list = get_vessel_list("dataset/vessels/")
    for vessel in vessels_list:
        if vessel_name == vessel["name"].upper(): # If the vessel name is the same as the one inputted by the user:
            selected_vessel_id = vessel["vessel_id"] # This is the ID of the vessel the user wants
                
    if selected_vessel_id == 0: # If the vessel wasn't found, return
        print("Manifest unavailable")
        return

    smallest_difference = -100000000

    # Open the file: port_calls.csv
    csv_filename = "dataset/port_calls.csv"
    with open(csv_filename, "r", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader) # Rows is a list. Each element is a list of columns. This is the port_calls table
    for row in rows:
        if row[1] == selected_vessel_id: # If this row contains the ID of the vessel the user selected:
            stripped_date = row[3].replace("-","")
            stripped_reference_date = reference_date.replace("-","")
            stripped_date = int(stripped_date) # Take the row date, and turn it into an int
            stripped_reference_date = int(stripped_reference_date) # Take the reference date, inputted by the user, and turn it into an int
            
            difference = stripped_reference_date - stripped_date 
            if difference <= 0 and difference > smallest_difference: # Check if the row date is the earliest date on or after the reference date
                smallest_difference = difference
                call_id = row[0] # If it is the earliest date, save the call ID from this row
                date = row[3]
                
    # Look through manifests
    manifests_path = "dataset/manifests/" #Finds the path to the manifests
    shipments_path = "dataset/shipments/" #Finds the path to the shipments
    manifest_file_names = os.listdir(manifests_path)
    shipment_list = []
    for file in manifest_file_names:
        with open(manifests_path+file, "r", encoding="utf-8") as manifest_file:
            # Find the manifest with matching call id
            manifest_raw = manifest_file.read()
            manifest_data = json.loads(manifest_raw)
            if manifest_data["call_id"] == call_id: 
             shipment_list = manifest_data["shipment_ids"]
    if shipment_list == []:
        print("No upcoming port calls found")
        return
    

    month = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[-2:])).strftime("%B")
    
    print(f"Manifest for {vessel_name.title()} | Call {call_id} | {date[-2:]} {month} {date[:4]}")

    resolved_weight = 0
    missing_records = 0

    for number, shipment in enumerate(shipment_list, start=1):
        shipment = "shipment-" + shipment[-4:] + ".json"
        try:
            with open(shipments_path+shipment, "r", encoding="utf-8") as shipment_file:
                shipment_raw = shipment_file.read()
                shipment_data = json.loads(shipment_raw)
                if "cargo_type" in shipment_data:
                    print(f"{number}. {shipment_data["shipment_id"]} | {shipment_data["customer"]} | {shipment_data["weight_kg"]} kg | {shipment_data["cargo_type"]}")
                else:
                    print(f"{number}. {shipment_data["shipment_id"]} | {shipment_data["customer"]} | {shipment_data["weight_kg"]} kg | NOT PROVIDED")
                resolved_weight += float(shipment_data["weight_kg"])
        except FileNotFoundError:
            print(f"{number}. {shipment_data["shipment_id"]} | MISSING RECORD")
            missing_records += 1
        declared_shipments = number
    print(f"Declared shipments: {declared_shipments}")
    print(f"Resolved weight: {resolved_weight:.2f} kg")
    print(f"Missing shipment records: {missing_records}")
