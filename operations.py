"""HarborFlow operational business rules.
Keep calculations and record-processing logic separate from user interaction
where practical.
"""

import datetime
import os
import json
import re
from data_access import get_dictionary_list, open_csv_file, write_csv_file, find_vessel
from text_tools import strip_date, find_non_repeat_seqs

def inspect_vessel(vessel_name, reference_date):
    selected_vessel_id = find_vessel(vessel_name)

    # FIND THE CORRECT PORT CALL ID
    call_id = 0
    smallest_difference = -999999999

    port_call_rows = open_csv_file("dataset/port_calls.csv")

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
        print("No upcoming port calls found.")
        return

    # FIND THE LIST OF SHIPMENTS THAT MATCH CALL ID IN MANIFESTS:       
    shipments_called = []

    manifest_list = get_dictionary_list("dataset/manifests/")
    for manifest in manifest_list:
        if manifest["call_id"] == call_id: 
            shipments_called += manifest["shipment_ids"]

    if shipments_called == []:
        print("Manifest unavailable.")
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
                    print(f"{count}. {shipment['shipment_id']} | {shipment['customer']} | {shipment['weight_kg']} kg | {shipment['cargo_type']}") # Print the data with cargo type
                else:
                    print(f"{count}. {shipment['shipment_id']} | {shipment['customer']} | {shipment['weight_kg']} kg | NOT PROVIDED") # Print the data without cargo type

                resolved_weight += float(shipment["weight_kg"]) # Make a total sum of the weight
                printed = True

        if not printed: # If there wasn't a record
            print(f"{count}. {called_id} | MISSING RECORD") # Print
            missing_records += 1

    declared_shipments = count

    # Print the remaining info to provide
    print(f"Declared shipments: {declared_shipments}")
    print(f"Resolved weight: {resolved_weight:.2f} kg")
    print(f"Missing shipment records: {missing_records}")


def classify_shipment(shipment):
    if shipment.get("hazardous") is True:
        return "CONTROLLED", "hazardous cargo"
    elif shipment.get("temperature_controlled") is True:
        return "COLD CHAIN", "temperature-controlled cargo"
    elif shipment.get("priority") == "EXPRESS" or shipment.get("weight_kg", 0) >= 5000:
        return "EXPEDITE", "express service"
    else:
        return "STANDARD", "standard service"


def identify_cargo():
    call_id = input("\nCall ID: ").strip().lower() # Ask user for a call ID
    match_found = False # Initialize a variable to track if a match is found

    manifest_dir = "dataset/manifests/" # Define the directory where manifests are stored
    if not os.path.exists(manifest_dir): # Check if the directory exists
        print(f"Error: The directory '{manifest_dir}' does not exist.")
        return

    for filename in os.listdir(manifest_dir): # Loop through all files in the manifests folder
        if filename.endswith(".json"): # Check if the file is a JSON file
            file_path = os.path.join(manifest_dir, filename) # Get the full path of the file
            try:
                with open(file_path, 'r') as f: # Open the JSON file
                    manifest = json.load(f) # Load the JSON data

                if manifest.get("call_id", "").lower() == call_id: # Check if the call ID matches
                    match_found = True

                    shipment_ids = manifest.get("shipment_ids", []) # Get the list of shipments
                    category_counts = {   # Initialize a dictionary to count categories
                        "CONTROLLED": 0,
                        "COLD CHAIN": 0,
                        "EXPEDITE": 0,
                        "STANDARD": 0
                    }

                    shipments_dir = "dataset/shipments/" # Define the directory where shipments are stored
                    for s_id in shipment_ids: # Loop through each shipment ID
                        formatted_filename = s_id.lower().replace("shp-", "shipment-") + ".json" # Format the shipment ID to match the filename in the shipments folder
                        shipment_path = os.path.join(shipments_dir, formatted_filename)

                        if not os.path.exists(shipment_path): # Check if the shipment file exists
                            continue
                        try:
                            with open(shipment_path, 'r') as sf:
                                shipment = json.load(sf)

                            shipment["hazardous"] = shipment.get("hazardous", False)
                            shipment["temperature_controlled"] = shipment.get("temperature_controlled", False)

                            category, reason = classify_shipment(shipment) # Classify the shipment
                            if category in category_counts:
                                category_counts[category] += 1

                            # Print in correct order
                            print(f"{s_id} | {category} | {reason}")

                        except Exception:
                            continue

                    # Print the category totals
                    print(f"Category totals: CONTROLLED={category_counts['CONTROLLED']}, COLD CHAIN={category_counts['COLD CHAIN']}, EXPEDITE={category_counts['EXPEDITE']}, STANDARD={category_counts['STANDARD']}")
                    return

            except json.JSONDecodeError:
                # Handle malformed manifest files
                print("Manifest unavailable")
                return
            except Exception:
                continue

    if not match_found:
        print("Port call not found.")


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
    header = ["customer", "shipment_count", "total_weight_kg", "express_count", "destinations"] # Create the header

    if not open_csv_file("exports/customer-profiles.csv"):  # If the file can't be found 
        os.makedirs("exports", exist_ok=True)
        write_csv_file("exports/customer-profiles.csv", [header, new_row]) # Create the CSV file with the header and new_row
    else:
        customer_rows = [header] + open_csv_file("exports/customer-profiles.csv") # If the file can be found...
        for i, customer in enumerate(customer_rows, start=0): # Cycle through each row
            if customer_name == customer[0]: # If our customer's name is already in the table:
                customer_found = True # Set customer_found to True
                customer_rows[i] = new_row # Update the row in our list of rows
        if not customer_found: # If the customer's name isn't in the table:
            customer_rows.append(new_row) # Add the new_row onto the list of rows

        write_csv_file("exports/customer-profiles.csv", customer_rows) # Write the updated list of rows into the CSV file
    print("Customer profile updated: exports/customer-profiles.csv")


def find_portcalls(month):
    if 0 < month < 10: # Change the format if input is 1 to 9
        zero_month = "0" + str(month)
    else: # Keep the old format
        zero_month = str(month)

    port_rows = open_csv_file("dataset/port_calls.csv") # Get port_calls.csv
    if not port_rows: # If the open_csv_file fct returned False, the file is missing
        print(f"Missing file") 
        return

    matching_port_calls = [] # Initiate empty list
    port_call_exists = False # Sets port_call to non-existent before we find any
    vessels_list = get_dictionary_list("dataset/vessels/") # Get vessels

    for row in port_rows: # Loops through all rows in port calls and checks which match our date
        date_row = row[3]
        if zero_month == date_row[5:7]:
            port_call_exists = True # Changes to true when a port call is found
            vessel_id = row[1] # Gets the vessel id from that row

            for vessel_dictionary in vessels_list: # Loops through the vessels and matches their id to their name
                if vessel_id == vessel_dictionary["vessel_id"]:
                    vessel_name = vessel_dictionary["name"]
                    break
            matching_port_calls.append((row, vessel_name)) # Adds both row and vessel_name to a list, in a tuple

    if not port_call_exists: # Prints a message if no port calls were found
        print("No port calls found.")
    else:
        month_letters = datetime.datetime(2000, month, 1).strftime("%B") # Turns the input month into letters
        print(f"Port calls in {month_letters}:")

        for row, vessel in matching_port_calls: # Loops through the matching rows and vessels and prints all the info
            day = row[3][8:10]
            year = row[3][0:4]
            port_code = row[2]
            call_id = row[0]
            print(f"- {day} {month_letters} {year} | {vessel} | {port_code} | {call_id}")


def sanitize_report():
    incidents_dir = "dataset/incidents/" # Define the directory where incident reports are stored
    if not os.path.exists(incidents_dir): # Check if the directory exists
        print("Incident directory not found.")
        return

    incidents = [] # Initialize a list to hold incident reports
    for filename in os.listdir(incidents_dir): # Loop through all files in the directory
        if filename.endswith(".json"):
            file_path = os.path.join(incidents_dir, filename)
            try:
                with open(file_path, 'r') as f: 
                    incident = json.load(f) 
                    incidents.append(incident) 
            except Exception:
                continue

    if incidents == []:
        print("No incident reports found.")
        return

    print("\nIncident Reports:")
    for idx, item in enumerate(incidents, start=1):
        print(f"{idx}. {item.get('title', 'Untitled')}")

    # Ask for selection after the list is displayed
    selected_incident = None
    while True:
        selected_incident_input = input("\nSelect incident list number: ").strip()
        if selected_incident_input.isdigit():
            choice_idx = int(selected_incident_input)
            if 1 <= choice_idx <= len(incidents):
                selected_incident = incidents[choice_idx - 1]
                break
        print("Error - Select a listed incident.")

    # Extract report text and incident_id
    report_text = selected_incident.get("report", "")
    incident_id = selected_incident.get("incident_id", "unknown")

    # Perform regular expression substitutions using standard re.sub()
    sanitized_text = report_text

    # 1. Container ID: 4 letters followed by 7 digits (case-insensitive letters)
    sanitized_text = re.sub(r'\b[A-Za-z]{4}\d{7}\b', '[CONTAINER]', sanitized_text)

    # 2. Seal number: SEAL- followed by 6 digits (case-insensitive)
    sanitized_text = re.sub(r'\b[sS][eE][aA][lL]-\d{6}\b', '[SEAL]', sanitized_text)

    # 3. Email address
    sanitized_text = re.sub(r'[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[EMAIL]', sanitized_text)

    # A report is considered changed when at least one substitution occurs
    if sanitized_text == report_text:
        print("Incident contains no share-sensitive identifiers.")
        return

    # Create output directory if necessary
    output_dir = "exports/sanitized/"
    os.makedirs(output_dir, exist_ok=True)

    # Save to file
    output_filename = f"{incident_id}-sanitized.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write(sanitized_text)

    print(f"Incident sanitized: {output_path}")


def analyze_longest_seq(directory, call):
    manifests_list = get_dictionary_list(directory)

    longest_seq = []
    manifest_found = False

    for manifest in manifests_list: # Cycle through each manifest
        if manifest["call_id"].upper() == call.upper(): # If this is the manifest the user typed a call ID for:
            manifest_found = True 
            codes_string = ",".join(manifest["event_codes"]) # Save a string of the event codes in this manifest for the print
            windows = find_non_repeat_seqs(manifest["event_codes"]) # Make a list of windows, or sequences with no repetition, from the event codes

    if not manifest_found:
        print("No manifest was found for this call ID.")
        return

    for window in windows: # Look through each window
        if len(window) > len(longest_seq): # If any window is longer than our longest sequence
            longest_seq = window # Our longest sequence becomes this window 

    # Print the results
    sequence_string = " -> ".join(longest_seq)
    print(f"\nEvent codes: {codes_string}")
    print(f"Longest stable sequence length: {len(longest_seq)}")
    print(f"Sequence: {sequence_string}")


def asses_weather(date_weather, weather_vessel_name):
    port_rows = open_csv_file("dataset/port_calls.csv") # Get port_calls.csv
    weather_rows = open_csv_file("dataset/weather.csv") # Get weather.csv
    vessel_files = get_dictionary_list("dataset/vessels/") # Get vessels
    smallest_difference = -9999999999 # Initialize smallest_difference
    vessel_id = 0 # Initialize vessel_id
    call_found = False # Initialize status of call_found
    forecast_available = False # Initialize status of forecast_available
    vessel_found = False # Initialize status of vessel_found

    for vessel in vessel_files: # Check if user input vessel exists
        if weather_vessel_name == vessel["name"].upper():
            vessel_id = vessel["vessel_id"]
            vessel_found = True
            break

    if not vessel_found: # Gives error message and returns to main menu
        print("Vessel not found.")
        return

    for row in port_rows: # Loops through the rows in port_rows and finds the matching date and vessel_id
        if vessel_id == row[1]:
            comparison_date = strip_date(row[3])
            date_weather_stripped = strip_date(date_weather)

            difference = date_weather_stripped - comparison_date # Calculate the difference between the date inputted by the user, and the date on this row

            if difference <= 0 and difference > smallest_difference: # Check if the row date is the earliest date on or after the reference date
                smallest_difference = difference
                port_code = row[2] # If it is the earliest date, save the call ID from this row
                date = row[3] # Save this to be printed at the end
                call_found = True # Changes status of call_found

    if not call_found: # Prints error message and return to menu
        print("No upcoming port calls found.")
        return

    month = datetime.datetime(int(date[:4]), int(date[5:7]), int(date[-2:])).strftime("%B") # Converts the month to letters

    for row in weather_rows: # Loops through the rows in weather.csv
        if port_code == row[0] and date == row[1]: # If both the port code and date matches in weather.csv, continue
            forecast_available = True # Changes status of forecast_available
            try: # Checks if the values are floats/integers
                wind_kmh = float(row[2]) 
                precipitation_mm = float(row[3])
                wave_height_m = float(row[4])

                # Print the first 2 info lines
                print(f"\n{weather_vessel_name.title()} | {port_code} | {date[-2:]} {month} {date[:4]}")
                print(f"Wind: {wind_kmh} km/h | Rain: {precipitation_mm} mm | Waves: {wave_height_m} m")

                recommendations = [] # Creates empty list
                # Checks and applies recommendations
                if wind_kmh >= 45:
                    recommendations.append("Suspend crane operations.")
                if wave_height_m >= 2.5:
                    recommendations.append("Arrange tug assistance.")
                if precipitation_mm >= 8 and wind_kmh < 45:
                    recommendations.append("Prepare covered handling.")
                if not recommendations:
                    recommendations.append("Normal operating plan.")

                # Prints the last info line
                print("Recommendation:", " ".join(recommendations))
            except ValueError:
                # Catches values that are strings, like "not-recorded" and informs the user
                print("Malformed forecast row.")

    # If there's no forecast for that date and port code
    if not forecast_available:
        print("Forecast unavailable")
        return


def search_reports():
    index_path = "dataset/incidents-index.json" # Define path for the cached search index
    incidents_dir = "dataset/incidents/" # Define directory where incident reports are stored

    if not os.path.exists(incidents_dir):
        print("Incident directory not found.")
        return

    # Check if cache needs to be rebuilt
    rebuild_cache = True # Default to True as a safeguard for missing, malformed, or outdated cache files
    if os.path.exists(index_path):
        try:
            cache_mtime = os.path.getmtime(index_path) # Get last modified time of the existing cache file
            latest_incident_mtime = max(
                os.path.getmtime(os.path.join(incidents_dir, f)) # Get the last modified time of each incident report file
                for f in os.listdir(incidents_dir) if f.endswith(".json") # Only consider JSON files
            )

            if cache_mtime >= latest_incident_mtime: # If the cache is newer than or equal to the latest incident report, we can use it
                rebuild_cache = False # If the cache is up-to-date, we don't need to rebuild it
        except Exception:
            rebuild_cache = True # Rebuild the cache if any error occurs.

    if rebuild_cache: # if the cache needs to be rebuilt, we will create a new index
        index_data = {} 
        titles_data = {}

        for filename in os.listdir(incidents_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(incidents_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        inc = json.load(f) # Open JSON file and load content into the dictionary
                        inc_id = inc.get("incident_id") # Get the incident ID
                        title = inc.get("title", "Untitled") # Get the title
                        report = inc.get("report", "") # Get the report text

                        if inc_id: # If the inc_id is missing, we skip this incident report
                            titles_data[inc_id] = title
                            words = set(re.findall(r'\b\w+\b', report.lower())) # Extract unique words using regex

                            for word in words:
                                if word not in index_data:
                                    index_data[word] = set()
                                index_data[word].add(inc_id)
                except Exception:
                    continue

        # Sort the incident IDs for each word        
        sorted_index = { 
            w: sorted(list(ids)) for w, ids in sorted(index_data.items()) 
        } 

        sorted_titles = { 
            inc_id: titles_data[inc_id] for inc_id in sorted(titles_data.keys()) 
        }

        # Create a dictionary to hold the sorted index and titles for caching
        cache_content = {
            "index": sorted_index,
            "titles": sorted_titles
        }

        os.makedirs(os.path.dirname(index_path), exist_ok=True) # Ensure the directory actually exists
        with open(index_path, 'w', encoding='utf-8') as cf: 
            json.dump(cache_content, cf)

    try: 
        with open(index_path, 'r', encoding='utf-8') as cf:
            cache = json.load(cf)
            word_index = cache.get("index", {})
            title_lookup = cache.get("titles", {})
    except Exception:
        print("Error reading incident index cache.")
        return

    # Get and normalize user query
    query = input("\nSearch incident reports: ").strip()
    if not query:
        return
    query_words = set(re.findall(r'\b\w+\b', query.lower()))

    if not query_words:
        return

    # Calculate scores by counting how many query words appear in each report
    score = {}
    for word in query_words:
        for inc_id in word_index.get(word, []):
            score[inc_id] = score.get(inc_id, 0) + 1

    # Prepare the list, results, for sorting by converting the score dictionary items into a list of tuples: (-score, inc_id)
    results = [(-s, inc_id) for inc_id, s in score.items()]
    results.sort() # In ascending order

    print(f"Matches for '{query}':")

    for neg_s, inc_id in results:
        s = -neg_s  # Convert back to positive score for display
        title = title_lookup.get(inc_id, "Untitled")
        print(f"- {inc_id} | score {s} | {title}")
