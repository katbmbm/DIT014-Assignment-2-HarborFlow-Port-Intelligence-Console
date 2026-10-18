from data_access import load_vessels
from operations import inspect_vessel, export_customer_profile, find_portcalls, analyze_longest_seq, asses_weather
from text_tools import validate_date, validate_month

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
                        category_counts = {    # Initialize a dictionary to count categories
                            "CONTROLLED": 0,
                            "COLD CHAIN": 0,
                            "EXPEDITE": 0,
                            "STANDARD": 0
                        }

                        shipments_dir = "dataset/shipments/" # Define the directory where shipments are stored
                        for s_id in shipment_ids: # Loop through each shipment ID NOTE: I chose s_id instead of shipment_id to avoid confusion with the shipment_ids variable
                            formatted_filename = s_id.lower().replace("shp-", "shipment-") + ".json" # There's probably a better way to do this... but I need to format the shipment ID to match the filename in the shipments folder
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
        print("Port call not found")

def sanitize_report():
    print("HI")

def search_reports():
    print("HI")

def main():
    choice = "0"
    while choice != "10":
        print("\nHARBORFLOW PORT INTELLIGENCE")
        print("1. List registered vessels")
        print("2. Inspect a vessel manifest")
        print("3. Identify priority cargo")
        print("4. Export a customer operations profile")
        print("5. Find port calls by month")
        print("6. Sanitize an incident report")
        print("7. Analyze the longest stable event sequence")
        print("8. Assess weather risk for upcoming calls")
        print("9. Search incident reports")
        print("10. Close console")

        choice = input("Select service: ")
        if choice == "1":
            load_vessels("dataset/vessels/") 

        elif choice == "2":
            load_vessels("dataset/vessels/")
            vessel_name = input("\nVessel name: ").upper().strip() # Ask user for a vessel name
            reference_date = input("Reference date (YYYY-MM-DD): ") # Ask the user for a reference date
            reference_date = validate_date(reference_date)
            inspect_vessel("dataset/vessels/", vessel_name, reference_date)

        elif choice =="3":
            identify_cargo()
            
        elif choice =="4":
            name = input("\nCustomer name: ").strip().title() # Asks for input
            export_customer_profile(name) # Runs the operation
            
        elif choice =="5":
            month_input = input("\nMonth (1-12): ") #Asks for input
            month = validate_month(month_input) #Validates the input
            find_portcalls(month) #Gives a list of the port calls in the chosen month or "no port calls found"
            
        elif choice =="6":
            sanitize_report()

        elif choice =="7":
            analyze_longest_seq("dataset/manifests/") # Runs the operation

        elif choice =="8":
            date_weather = input("\nReference date (YYYY-MM-DD): ")
            date_weather = validate_date(date_weather)
            weather_vessel_name = input("Vessel name: ").upper().strip()
            asses_weather(date_weather, weather_vessel_name)

        elif choice =="9":
            search_reports()

        elif choice != "10":
            print("Error - Select a service from 1 to 10.")
    print("\nConsole closed. HarborFlow operational data remains safe.\n")
      
       
if __name__ == "__main__":
   main()
