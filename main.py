import json
import csv
import os

def load_vessels(directory):
    skipped = 0 # Start a counter for skipped vessels at 0

    filenames = os.listdir(directory) # Find the filenames in the directory

    print("\nRegistered HarborFlow vessels:")
    
    
    for file in filenames: # Loop through each name
        path = directory+file 
        if not load_json(path): # Run load_json for each file and check if it returned false
            skipped += 1 # If it returned false, report a skipped vessel

    print(f"Skipped vessel files: {skipped}")


def load_json(path):
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


def inspect_vessel():
    directory = "dataset/vessels/"
    filenames = os.listdir(directory)
    vessel_name = input("Vessel name: ").upper().strip()
    vessels_list = []
    for file in filenames: # Loop through each name
        path = directory+file 
        try:
            with open(path, "r", encoding="utf-8") as file:
                raw_text = file.read() # Read the json file
                try:
                    vessel = json.loads(raw_text) # Convert to dictonary if possible
                    vessels_list.append(vessel["name"].upper()) # Adds all dictionaries to a list
                    if vessel_name == vessel["name"].upper():
                        selected_vessel_id = vessel["vessel_id"]
            
                except json.decoder.JSONDecodeError: 
                    pass
        
        except FileNotFoundError:
            print(f"Missing file")
                
        if vessel_name not in vessels_list:
         print("Manifest unavailable")
         return
        

    reference_date = input("Reference date (YYYY-MM-DD): ")
    while not (reference_date[0:4].isdigit() and reference_date[5:7].isdigit() and reference_date[8:10].isdigit() and reference_date[4] == "-" and reference_date[7] == "-" and len(reference_date) == 10):
        print("Invalid reference date")
        reference_date = input("Reference date (YYYY-MM-DD): ")

    
    
    smallest_difference = 10000
    csv_filename = "dataset/port_calls.csv"
    with open(csv_filename, "r", newline="") as file:
     reader = csv.reader(file)
     rows = list(reader)
    for row in rows:
        if row[1] == selected_vessel_id:
            stripped_date = row[3].replace("-","")
            stripped_reference_date = reference_date.replace("-","")
            stripped_date = int(stripped_date)
            stripped_reference_date = int(stripped_reference_date)
            difference = stripped_reference_date - stripped_date
            if difference < smallest_difference:
                smallest_difference = difference
                call_id = row[0]
    manifests = "dataset/manifests"
    with open(manifests, "r", encoding="utf-8") as manifest_file:
        # Look through manifests and find the one with matching call id



            

def identify_cargo():
    print("HI")

def identify_profile():
    print("HI")

def find_portcalls():
    print("HI")

def sanitize_report():
    print("HI")

def analyze_sequence():
    print("HI")

def asses_weather():
    print("HI")

def search_reports():
    print("HI")


def main():
    choice = "11"
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
            inspect_vessel()
        elif choice =="3":
            identify_cargo()
        elif choice =="4":
            identify_profile()
        elif choice =="5":
            find_portcalls()
        elif choice =="6":
            sanitize_report()
        elif choice =="7":
            analyze_sequence()
        elif choice =="8":
            asses_weather()
        elif choice =="9":
            search_reports()
        elif choice != "10":
            print("Error - Select a service from 1 to 10.")
    print("Console closed. HarborFlow operational data remains safe.")
      
       
if __name__ == "__main__":
   main()

