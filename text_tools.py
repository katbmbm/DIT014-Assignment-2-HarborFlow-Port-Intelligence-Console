"""Regex sanitization, stable-sequence, and incident-index functions."""

def validade_date(reference_date):
    while not (reference_date[0:4].isdigit() and reference_date[5:7].isdigit() and reference_date[8:10].isdigit() and reference_date[4] == "-" and reference_date[7] == "-" and len(reference_date) == 10):
        print("Error - Date must use YYYY-MM-DD")
        reference_date = input("Reference date (YYYY-MM-DD): ")
    return reference_date

def strip_date(date):
    stripped_date = str(date).replace("-","")
    return int(stripped_date)
