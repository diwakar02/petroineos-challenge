#!/usr/bin/env python

import unittest
import pandas as pd
from unittest.mock import patch
import requests
import sys
sys.path.append('../')
from petroineos.petroineos_data_module import transform_quarterly_data


class TestDataFrame(unittest.TestCase):

    def setUp(self):
        # Sample DataFrame for testing
        dataframe_columns = ['Quarter', 'Indigenous_production', 'Indigenous_production_Crude_oil', 'Indigenous_production_NGLs', 
                    'Indigenous_production_Feedstocks', 'Imports', 'Imports_Crude oil_&_NGLs', 'Imports_Feedstocks',
                    'Exports', 'Exports_Crude oil_&_NGLs', 'Exports_Feedstocks', 'Stock_change', 'Transfers', 
                    'Total_supply', 'Statistical_difference', 'Total_demand', 'Transformation', 'Petroleum_refineries',
                    'Energy_industry_use', 'Oil_&_gas_extraction']
        local_xls_file_name = 'ET_3.1_SEP_24.xlsx'
        output_dir = 'cleaned_quarterly_data'
        self.df = transform_quarterly_data(local_xls_file_name, dataframe_columns, output_dir)

    def test_columns_present(self):
        # Define the required columns
        required_columns = self.dataframe_columns
        # Check if the DataFrame contains the required columns
        self.assertTrue(all(col in self.df.columns.values.tolist() for col in required_columns), "Missing required columns")

    def test_missing_values(self):
        # Maximum allowed missing values per column
        max_missing_values_per_column = 1
        # Check for missing values in each column
        missing_values = self.df.isnull().sum()
        for column in self.df.columns:
            self.assertLessEqual(missing_values[column], max_missing_values_per_column, f"Too many missing values in column {column}")

    def test_row_count(self):
        # Minimum number of rows threshold
        min_rows = 100
        # Check the number of rows in the DataFrame
        self.assertGreaterEqual(len(self.df), min_rows, f"DataFrame has fewer than {min_rows} rows")

if __name__ == '__main__':
    unittest.main()