from data_access import load_vessels, find_vessel
from operations import inspect_vessel, export_customer_profile, find_portcalls, analyze_longest_seq, asses_weather, identify_cargo, sanitize_report, search_reports
from text_tools import validate_date, validate_month

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
            found_vessel = find_vessel(vessel_name)
            if not found_vessel:
                main()
                return
            reference_date = input("Reference date (YYYY-MM-DD): ") # Ask the user for a reference date
            reference_date = validate_date(reference_date)
            inspect_vessel(vessel_name, reference_date)

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
            call = input("\nCall ID: ")
            analyze_longest_seq("dataset/manifests/", call) # Runs the operation

        elif choice =="8":
            weather_vessel_name = input("Vessel name: ").upper().strip()
            date_weather = input("Reference date (YYYY-MM-DD): ")
            date_weather = validate_date(date_weather)
            asses_weather(date_weather, weather_vessel_name)

        elif choice =="9":
            search_reports()

        elif choice != "10":
            print("Error - Select a service from 1 to 10.")
    print("\nConsole closed. HarborFlow operational data remains safe.\n")
      
       
if __name__ == "__main__":
   main()
