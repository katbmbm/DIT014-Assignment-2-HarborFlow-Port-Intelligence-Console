HARBORFLOW PORT INTELLIGENCE CONSOLE - TEAM README

Run instructions
----------------
Command: python harborflow2.py
Python version tested: 3.14.7

Team members and concrete contributions
---------------------------------------
Name: Katherine
Contribution: Wrote the code for tasks 1, 4 and 7. Contributed to the code for task 2.

Name: Kevi
Contribution: Wrote the code for tasks 3, 6 and 9. Contributed to the code for task 1.

Name: Frida
Contribution: Wrote the main function and the code for tasks 2, 5 and 8. Contributed to the code for task 1.


Architecture
------------
main.py responsibilities: Runs the main menu, mostly calls upon functions in text_tools and operations.py, depending on the user's choice and asks the user for inputs (which are passed into the functions).
data_access.py responsibilities: Deals with opening, reading, writing on and processing of files.
operations.py responsibilities: Is called upon from main.py to execute the principal tasks, calculations, computations and prints. Calls upon functions in data_access.py and text_tools.py.
text_tools.py responsibilities: Deals with processing strings and validating user inputs.


File and error-handling design
------------------------------
How paths are resolved: The paths are consistently passed into functions as parameters and are always relative paths.
How malformed or missing input is handled: Inputs are passed into functions where the code tests for any malformed or missing inputs, runs an error message and then safely returns to the main.
How generated files are updated safely: Generated files and exports are written safely using "with open(...)", which ensure files are properly closed even if an error occurs during writing.


Known limitations
-----------------
None known.
