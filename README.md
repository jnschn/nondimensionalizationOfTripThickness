# nondimensionalizationOfTripThickness
This script uses the Falkner-Skan library by peterdsharpe: https://github.com/peterdsharpe/Falkner-Skan.
The purpose of this script is, to nondimensionalize the thickness of a zigzag tape on an airfoil. It uses simulation data from XFLR5 at the position of the tape and the thickness of the tape, to calculate a Reynolds Number representing the thickness (Re_k).
It takes a CSV-file, with data from XFLR5, as shown in example.csv, calculates the Re_k and adds it to the file. 
