"""HarborFlow operational business rules.

Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import datetime

from data_access import get_dictionary_list, open_csv_file, write_csv_file
from text_tools import strip_date, validate_month

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


def find_portcalls(month):
    month = validate_month(month) #Checks if month is valid
    if 0 < month < 10: #Change the format if input is 1 to 9
        zero_month = "0" + str(month)
    else: #Keep the old format
        zero_month = str(month)

    port_rows = open_csv_file("dataset/port_calls.csv") #Get port_calls.csv
    if not port_rows: # If the open_csv_file fct returned False, the file is missing
            print(f"Missing file") 
            return

    matching_port_calls = [] #Initiate empty list
    port_call_exists = False #Sets port_call to non-existent before we find any
    vessels_list = get_dictionary_list("dataset/vessels/") #Get vessels
    for row in port_rows: #Loops through all rows in port calls and checks which match our date
        date_row = row[3]
        if zero_month == date_row[5:7]:
            port_call_exists = True #Changes to true when a port call is found
            vessel_id = row[1] #Gets the vessel id from that row
           
            for vessel_dictionary in vessels_list: #Loops through the vessels and matches their id to their name
                if vessel_id == vessel_dictionary["vessel_id"]:
                    vessel_name = vessel_dictionary["name"]
                    break
            matching_port_calls.append((row, vessel_name)) #Adds both row and vessel_name to a list, in a tuple
    if not port_call_exists: #Prints a message if no port calls were found
        print("No port calls found")
    else:
        month_letters = datetime.datetime(2000, month, 1).strftime("%B") #Turns the input month into letters
        print(f"Port calls in {month_letters}:")
    
        for row, vessel in matching_port_calls: #Loops through the matching rows and vessels and prints all the info
            day = row[3][8:10]
            year = row[3][0:4]
            port_code = row[2]
            call_id = row[0]
            print(f"- {day} {month_letters} {year} | {vessel} | {port_code} | {call_id}")


def analyze_longest_seq(directory):
    manifests_list = get_dictionary_list(directory)

    longest_seq = []

    for manifest in manifests_list: # Cycle through each manifest
        windows = [[]] # Create a windows list with an empty window list inside of it
        index = 0 # Start an index for the windows at 0
        for code in manifest["event_codes"]: # Cycle through each event code in the manifest
            if code not in windows[index]: # If the code isn't in our window
                windows[index].append(code) # Add the code to the window
            else: # If the code is already in the window
                windows.append([]) # Make a new window
                index += 1 # We will start working from the new window
                windows[index].append(code) # Add the code to this window

        for window in windows: # Look through each window in this manifest
            if len(window) > len(longest_seq): # If any window is longer than our longest sequence
                longest_seq = window # Our longest sequence becomes this window 
                codes_string = ",".join(manifest["event_codes"]) # Save a string of the event codes in this manifest for the print

    # Print the results
    sequence_string = " -> ".join(longest_seq)
    print(f"\nEvent codes: {codes_string}")
    print(f"Longest stable sequence length: {len(longest_seq)}")
    print(f"Sequence: {sequence_string}")


def asses_weather(date_weather, weather_vessel_name):
    port_rows = open_csv_file("dataset/port_calls.csv") #Get port_calls.csv
    weather_rows = open_csv_file("dataset/weather.csv") #Get weather.csv
    vessel_files = get_dictionary_list("dataset/vessels/") #Get vessels
    smallest_difference = -9999999999 #Initalize smallest_difference
    vessel_id = 0 #Initalize vessel_id
    call_found = False #Initalize status of call_found
    forecast_available = False #Initalize status of forecast_available
    vessel_found = False #Initalize status of vessel_found

    for vessel in vessel_files: #Check if user input vessel exists
        if weather_vessel_name == vessel["name"].upper():
            vessel_id = vessel["vessel_id"]
            vessel_found = True

    if not vessel_found: #Gives error message and returns to main menu
        print("Vessel not found")
        return

    for row in port_rows: #Loops through the rows in port_rows and finds the matching date and vessel_id
        if vessel_id == row[1]:
            comparison_date = strip_date(row[3])
            date_weather = strip_date(date_weather)
        
            difference = date_weather - comparison_date # Calculate the difference between the date inputted by the user, and the date on this row
                    
            if difference <= 0 and difference > smallest_difference: # Check if the row date is the earliest date on or after the reference date
                smallest_difference = difference
                port_code = row[2] # If it is the earliest date, save the call ID from this row
                date = row[3] # Save this to be printed at the end
                call_found = True #Changes status of call_found
    
    if not call_found: #Prints error message and return to menu
        print("No upcoming port calls found.")
        return

    month = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[-2:])).strftime("%B") #Converts the month to letters

    for row in weather_rows: #Loops through the rows in weather.csv
        if port_code == row[0] and date == row[1]: #If both the port code and date matches in weather.csv, continue
            forecast_available = True #Changes status of forecast_available
            try: #Checks if the values are floats/integers
                wind_kmh = float(row[2]) 
                precipitation_mm = float(row[3])
                wave_height_m = float(row[4])

                #Print the first 2 info lines
                print(f"\n{weather_vessel_name.title()} | {port_code} | {date[-2:]} {month} {date[:4]}")
                print(f"Wind: {wind_kmh} km/h | Rain: {precipitation_mm} mm | Waves: {wave_height_m} m")

                recommendations = [] #Creates empty list
                #Checks and applies recommendations
                if wind_kmh >= 45:
                    recommendations.append("Suspend crane operations.")
                if wave_height_m >= 2.5:
                    recommendations.append("Arrange tug assistance.")
                if precipitation_mm >= 8 and wind_kmh < 45:
                    recommendations.append("Prepare covered handling.")
                if not recommendations:
                    recommendations.append("Normal operating plan.")

                #Prints the last info line
                print("Recommendation:", " ".join(recommendations))
            #Catches values that are strings, like "not-recorded" and informs the user
            except ValueError:
                print("Malformed forecast row.")

    #If there's no forecast for that date and port code
    if not forecast_available:
        print("Forecast unavailable")
        return
