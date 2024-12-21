#!/usr/bin/env python3

import geopandas as gpd
import json


def main(df, json_filename,column_name):
    # Load GeoJSON data into a GeoPandas DataFrame
    
    # Extract unique values from the specified column
    unique_values = df[column_name].unique()

    # Create a dictionary with keys as 1, 2, 3, ... and values as the unique values
    values_dict = {str(i+1): value for i, value in enumerate(unique_values)}

    # Save to JSON file
    with open(json_filename, 'w') as f:
        json.dump(values_dict, f)