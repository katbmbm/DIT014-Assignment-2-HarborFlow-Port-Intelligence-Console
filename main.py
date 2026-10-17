import json
import csv
import os
import datetime

from data_access import load_vessels
from operations import inspect_vessel
from text_tools import validade_date

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
            load_vessels("dataset/vessels/")
            vessel_name = input("\nVessel name: ").upper().strip() # Ask user for a vessel name
            reference_date = input("Reference date (YYYY-MM-DD): ") # Ask the user for a reference date
            validade_date(reference_date)
            inspect_vessel(vessel_name, reference_date)

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

