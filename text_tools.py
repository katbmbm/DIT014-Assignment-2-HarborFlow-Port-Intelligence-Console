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
   valid = False
    while not valid:
        try:
            month_int = int(month)
            if 1 <= month_int <= 12:
                return month_int
            print("Error - Enter a month from 1 to 12.")
        except ValueError:
            print("Error - Enter a month from 1 to 12.")
            
        month = input("Month (1-12): ")

def find_non_repeat_seqs(seq_list):
    windows = [[]] # Create a windows list with an empty window list inside of it
    index = 0 # Start an index for the windows at 0

    for item in seq_list: # Cycle through each item in the seq list
        if item not in windows[index]: # If the item isn't in our window
            windows[index].append(item) # Add the item to the window
                    
        else: # If the item is already in the window
            for inner_index in range(len(windows[index])-1): # Cycle through the indecies for the items inside the window
                if windows[index][inner_index] == item: # If you reach the item that was repeated:
                    windows.append(windows[index-1][inner_index+1:]) # Create a new window that starts just after the repeated item
                    index += 1 # We will start working from the new window
                    windows[index].append(item) # Add the item to this window

    return windows # Return a list of sequences without repetition, made from the list inputted
    
