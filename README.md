QuestBlue API

Written by Alex Marquardt

For internal use at HD Tec Solutions

July 2023

Version 1.3.2

This program is intended for internal use for processing and collecting phone data. The program is not designed or intended for distribution. To distribute this software the user might need to alter or add to the code. To run the software run “questMain.exe”. The Main file uses a specially designed library called questblueAPI.py which is located in the lib directory. This is the location of the functions that interact with the Quest Blue API.


For assistance or to contribute to the project contact Alex Marquardt
alex.marquardt@hdtecsolutions.com


Change Log

- Changes
    Add:
        Added Config File - Now you can edit multiple global variables for the whole program in 1 file. Located in ./config/config.py
        Added Multi-Threading - Users can select how many threads they would like to use when running the scripts. Can be edited in the config file under max_threads
        Added Remember Me - Allows program to remember user login
        Added New Exe - The Exe was divided from the GUI python file. 

    Fixes:
        Fixed output spreadsheet printing header multiple times
        Fixed output path text size

What's Next?
    Adding:
        Output Rework - The output sheet will be reworked to use pandas. This will allow for a more in-depth breakdown of data including specific did activity per trunk.
        Settings - This will allow the user to directly edit the config file in the program
    
    