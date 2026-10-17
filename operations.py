"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import json
import csv
import os
import datetime

from data_access import get_dictionary_list, open_csv_file, write_csv_file
from text_tools import strip_date

def inspect_vessel(directory, vessel_name, reference_date):
    vessels_list = []
    
    # FIND THE VESSEL'S ID
    selected_vessel_id = 0
    
    vessels_list = get_dictionary_list(directory) # Get a list of all the vessel dictionaries

    for vessel in vessels_list:
        if vessel_name == vessel["name"].upper(): # If the vessel name is the same as the one inputted by the user:
            selected_vessel_id = vessel["vessel_id"] # This is the ID of the vessel the user wants
                
    if selected_vessel_id == 0: # If the vessel wasn't found, return
        print("Manifest unavailable")
        return

    # FIND THE CORRECT PORT CALL ID
    call_id = 0
    smallest_difference = -999999999

    port_call_rows =  open_csv_file("dataset/port_calls.csv")

    if not port_call_rows: # If the open_csv_file fct returned False, the file is missing
        print(f"Missing file") 
        return
    
    for row in port_call_rows:
        if row[1] == selected_vessel_id: # If this row contains the ID of the vessel the user selected:
            comparison_date = strip_date(row[3])
            reference_date = strip_date(reference_date)

            difference = reference_date - comparison_date # Calculate the difference between the date inputted by the user, and the date on this row
            
            if difference <= 0 and difference > smallest_difference: # Check if the row date is the earliest date on or after the reference date
                smallest_difference = difference
                call_id = row[0] # If it is the earliest date, save the call ID from this row
                date = row[3] # Save this to be printed at the end
    
    if call_id == 0:
        print("No call ID was found to match the information provided.")
        return
    
    # FIND THE LIST OF SHIPMENTS THAT MATCH CALL ID IN MANIFESTS:       
    shipments_called = []
    
    manifest_list = get_dictionary_list("dataset/manifests/")
    for manifest in manifest_list:
        
        if manifest["call_id"] == call_id: 
            shipments_called += manifest["shipment_ids"]

    if shipments_called == []:
        print("No upcoming port calls found")
        return

    # PRINT THE DATA FOUND:
    month = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[-2:])).strftime("%B")
    print(f"Manifest for {vessel_name.title()} | Call {call_id} | {date[-2:]} {month} {date[:4]}")

    # Set these counters to 0
    resolved_weight = 0
    missing_records = 0

    shipment_list = get_dictionary_list("dataset/shipments/")
 
    for count, called_id in enumerate(shipments_called, start=1): # For every ID in the shipments called list:
        printed = False

        for shipment in shipment_list:
            if called_id == shipment["shipment_id"]: # Find the corresponding shipment data
                
                if "cargo_type" in shipment: # Check if cargo type is provided
                    print(f"{count}. {shipment["shipment_id"]} | {shipment["customer"]} | {shipment["weight_kg"]} kg | {shipment["cargo_type"]}") # Print the data with cargo type
                else:
                    print(f"{count}. {shipment["shipment_id"]} | {shipment["customer"]} | {shipment["weight_kg"]} kg | NOT PROVIDED") # Print the data without cargo type
                
                resolved_weight += float(shipment["weight_kg"]) # Make a total sum of the weight
                
                printed = True
        if not printed: # If there wasn't a record
            print(f"{count}. {shipment["shipment_id"]} | MISSING RECORD") # Print
            missing_records += 1
        
        declared_shipments = count

    # Print the remaining info to provide
    print(f"Declared shipments: {declared_shipments}")
    print(f"Resolved weight: {resolved_weight:.2f} kg")
    print(f"Missing shipment records: {missing_records}")


def export_customer_profile(customer_name):
    shipment_list = get_dictionary_list("dataset/shipments/")

    customers_shipments = [] # Start the list of the customer's shipments as empty

    for shipment in shipment_list:
        if shipment["customer"].title() == customer_name: # If the shipment is under the customer's name:
            customers_shipments.append(shipment) # Add it to their list

    if customers_shipments == []: # If the list is still empty
        print("Customer not found.") # No shipments were found for this customer, so we return
        return
    
    # Set our variables' initial values
    shipment_count = len(customers_shipments) 
    total_weight = 0
    express_count = 0
    destinations = []

    for shipment in customers_shipments: # For each one of the customer's shipments:
        total_weight += shipment["weight_kg"] # Add weight to total sum
 
        if shipment["priority"].upper() == "EXPRESS": # Count how many EXPRESS shippings there are
            express_count += 1

        if shipment["destination"] not in destinations: # If there's a destination not yet in the list of destinations:
            destinations.append(shipment["destination"]) # Add it to the list

    destinations = "|".join(destinations) # Turn the destination list into a string joined by "|"

    
    new_row = [customer_name, shipment_count, total_weight, express_count, destinations] # Use these values to assemble a new row for our customer-profiles table

    customer_found = False 

    if not open_csv_file("exports/customer-profiles.csv"):  # If the file can't be found  
        header = ["customer", "shipment_count", "total_weight_kg", "express_count", "destinations"] # Create the header
        write_csv_file("exports/customer-profiles.csv", [header, new_row]) # Create the CSV file with the header and new_row
    else:
        customer_rows = open_csv_file("exports/customer-profiles.csv") # If the file can be found...
        for i, customer in enumerate(customer_rows, start=0): # Cycle through each row
            if customer_name == customer[0]: # If our customer's name is already in the table:
                customer_found = True # Set customer_found to True
                customer_rows[i] = new_row # Update the row in our list of rows
        if not customer_found: # If the customer's name isn't in the table:
            customer_rows.append(new_row) # Add the new_row onto the list of rows
        
        write_csv_file("exports/customer-profiles.csv", customer_rows) # Write the updated list of rows into the CSV file
    print("Customer profile updated: exports/customer-profiles.csv")
        


