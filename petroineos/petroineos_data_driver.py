#!/usr/bin/env python

import argparse
from petroineos_data_module import requests_retry_session, get_last_modified, save_last_modified, \
                                   has_file_changed, download_file, transform_quarterly_data, logger


url = 'https://www.gov.uk/government/statistics/oil-and-oil-products-section-3-energy-trends'
dataframe_columns = ['Indigenous_production', 'Indigenous_production_Crude_oil', 'Indigenous_production_NGLs', 
                    'Indigenous_production_Feedstocks', 'Imports', 'Imports_Crude oil_&_NGLs', 'Imports_Feedstocks',
                    'Exports', 'Exports_Crude oil_&_NGLs', 'Exports_Feedstocks', 'Stock_change', 'Transfers', 
                    'Total_supply', 'Statistical_difference', 'Total_demand', 'Transformation', 'Petroleum_refineries',
                    'Energy_industry_use', 'Oil_&_gas_extraction']
local_xls_file_name = 'ET_3.1_SEP_24.xlsx'
last_modified_file = 'last_modified.txt'

if __name__ == "__main__":
    ''' Main driver method to run the data cleansing module'''
    try:
        parser = argparse.ArgumentParser(description="Enter the name of directory for the output")
        parser.add_argument('output_dir', type=str, help="The location of the directory in the local storage")
        args = parser.parse_args()

        if has_file_changed(url, last_modified_file):
            logger.info('File has been changed. Cleaning is required. Entering cleansing mode...')
            transform_quarterly_data(local_xls_file_name, dataframe_columns, args.output_dir)
            logger.info('CSV file saved successfully. You can now quit')
        else:
            download_file(url)
            transform_quarterly_data(local_xls_file_name, dataframe_columns, args.output_dir)
    except Exception as e:
        logger.error("An error occurred while doing transformation" + str(e))


