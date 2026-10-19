"""Regex sanitization, stable-sequence, and incident-index functions."""

def validate_date(reference_date):
    while not (reference_date[0:4].isdigit() and reference_date[5:7].isdigit() and reference_date[8:10].isdigit() and reference_date[4] == "-" and reference_date[7] == "-" and len(reference_date) == 10):
        print("Error - Date must use YYYY-MM-DD")
        reference_date = input("Reference date (YYYY-MM-DD): ")
    return reference_date


def strip_date(date):
    stripped_date = str(date).replace("-","")
    return int(stripped_date)


def validate_month(month):
    while True:
        try:
            month = int(month)
            if 1 <= month <= 12:
                return month
            else:
                print("Error - Enter a month from 1 to 12")
                month = input("Month (1-12): ")
        except ValueError:
            print("Error - Enter a month from 1 to 12")
            month = input("Month (1-12): ")

def sanitize_report():
    incidents_dir = "dataset/incidents/" # Define the directory where incident reports are stored
    if not os.path.exists(incidents_dir): # Check if the directory exists
        print("Incident directory not found.")
        return

    incidents = [] # Initialize a list to hold incident reports
    for filename in os.listdir(incidents_dir): # Loop through all files in the
        if filename.endswith(".json"):
            file_path = os.path.join(incidents_dir, filename)
            try:
                with open(file_path, 'r') as f: 
                    incident = json.load(f) 
                    incidents.append(incident) 
            except Exception:
                continue

    if not incidents:
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
    
    
    
    
