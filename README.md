# petroineos-challenge
data pipeline challenge for petroineos London

# STRUCTURE
The structure tree is as follows:


![image](https://github.com/user-attachments/assets/2030a366-ce6d-4482-a5a5-c5e6363510b9)


The petroineos folder is build as a pip module and can be downloaded as "pip install .' locally
The submodules contains the petroineos source files which contains a petroineos_data_driver file which acts as an Entry point to the petroineos_data_module
The petroineos_data_module contains functions to check for file updates, downloading the excel file from webURL and transforming the excel file to a dataframe using pandas


USAGE:
python ./petroineos_data_driver "your-directory-name"

ASSUMPTIONS:
1. Only working for Quarter work sheet.
2. Transformation code is not asynchronos as it is only dealing with small file
3. After checking the excel file, the tranpose needs to be performed to return quarters to datetime objects
   

