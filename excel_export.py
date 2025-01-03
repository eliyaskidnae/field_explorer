#!/usr/bin/env python3
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from filter import *
import os
import click

filename = None  # Path to the shapefile
geojson_df = None  # GeoPandas DataFrame
filter_code = None  # Column name to filter the data
is_bio = None  # Type of data


def get_data_category():
    global filename
    global geojson_df
    global filter_code
    global is_bio
    # Read the JSON file and send its content as the response
    json_filename = f"{os.path.splitext(filename)[0]}.json"
    # Extract unique values from the specified column
    unique_values = geojson_df[filter_code].unique()
    # Create a dictionary with keys as 1, 2, 3, ... and values as the unique values
    values_dict = {str(i + 1): value for i, value in enumerate(unique_values)}
    # Save to JSON file
    with open(json_filename, "w") as f:
        json.dump(values_dict, f)

    with open(json_filename, "r") as f:
        code_cultu_data = json.load(f)
        print("filname", json_filename)

    response = {"data_file_name": filename, "code_cultu_data": code_cultu_data}
    return response


def filter_geojson(code_cultu, surface_ha_min=None, surface_ha_max=None):
    global filename
    global geojson_df
    global filter_code
    global is_bio

    filter_surface = "surface_ha" if "surface_ha" in geojson_df.columns else "SURF_PARC"
    filtered_df = geojson_df[
        (geojson_df[filter_code] == code_cultu)
        & ((surface_ha_min is None) | (geojson_df[filter_surface] >= surface_ha_min))
        & ((surface_ha_max is None) | (geojson_df[filter_surface] <= surface_ha_max))
    ]

    # Sort the filtered DataFrame
    filtered_df.sort_values(by=filter_surface, ascending=False, inplace=True)

    # Calculate the required statistics
    total_features = len(filtered_df)
    features_lt_1 = len(filtered_df[filtered_df[filter_surface] < 1])
    total_area_lt_1 = filtered_df[filtered_df[filter_surface] < 1][filter_surface].sum()
    features_1_to_3 = len(
        filtered_df[
            (filtered_df[filter_surface] >= 1) & (filtered_df[filter_surface] < 3)
        ]
    )
    total_area_lt_1_to_3 = filtered_df[
            (filtered_df[filter_surface] >= 1) & (filtered_df[filter_surface] < 3)
        ][filter_surface].sum()

    features_3_to_8 = len(
        filtered_df[
            (filtered_df[filter_surface] >= 3) & (filtered_df[filter_surface] < 8)
        ]
    )
    total_area_3_to_8 = filtered_df[
            (filtered_df[filter_surface] >= 3) & (filtered_df[filter_surface] < 8)
        ][filter_surface].sum()
    features_gt_8 = len(filtered_df[filtered_df[filter_surface] >= 8])

    total_area_gt_8 = filtered_df[filtered_df[filter_surface] >= 8][filter_surface].sum()

    # mean and median
    mean_surface = filtered_df[filter_surface].mean()
    median_surface = filtered_df[filter_surface].median()

    # Convert the filtered DataFrame to JSON
    filtered_features = filtered_df.head(30).to_json()

    # Create the response dictionary
    response = {
        "total_features": total_features,
        "features_lt_1": features_lt_1,
        "total_area_lt_1": total_area_lt_1,
        "features_1_to_3": features_1_to_3,
        "total_area_lt_1_to_3": total_area_lt_1_to_3,
        "features_3_to_8": features_3_to_8,
        "total_area_3_to_8": total_area_3_to_8,
        "features_gt_8": features_gt_8,
        "total_area_gt_8": total_area_gt_8,
        "filtered_features": json.loads(filtered_features),
        "all_features": len(geojson_df),
        "data_file_name": filename,
        "mean_surface": mean_surface,
        "median_surface": median_surface,
    }
    return response


def prepare_data_for_export():
    global filename
    global geojson_df
    global filter_code
    global is_bio

    json_filename = f"{os.path.splitext(filename)[0]}.json"
    with open(json_filename) as f:
        data = json.load(f)
        result = []
        for _, code in data.items():
            response = filter_geojson(code)
            row = {
                "code_cultu": code,
                "total_features": response["total_features"],
                "features_lt_1": response["features_lt_1"],
                "total_area_lt_1": response["total_area_lt_1"],
                "features_1_to_3": response["features_1_to_3"],
                "total_area_lt_1_to_3": response["total_area_lt_1_to_3"],
                "features_3_to_8": response["features_3_to_8"],
                "total_area_3_to_8": response["total_area_3_to_8"],
                "features_gt_8": response["features_gt_8"],
                "total_area_gt_8": response["total_area_gt_8"],
                "mean_surface": response["mean_surface"],
                "median_surface": response["median_surface"],
                "data_source": filename,
                "type": is_bio,
            }
            result.append(row)

        return result


default_filename = "data/RPG_2-2__GPKG_LAMB93_FXX_2023-01-01/PARCELLES_GRAPHIQUES_4326.pkl"

@click.command()
@click.option(
    "--filepath",
    default=default_filename,
    help="Path of the shapefile to load",
    type=str,
)
def get_filename(filepath):
    print("Filepath:", filepath)
    return filepath


def main():
    global filename
    global geojson_df
    global filter_code
    global is_bio

    filename = get_filename(standalone_mode=False)
    geojson_df = pd.read_pickle(filename)
    print("Filepath:", filename)
    # geojson_df = gpd.read_file(filename)
    filter_code = "code_cultu" if "code_cultu" in geojson_df.columns else "CODE_CULTU"
    is_bio = "bio" if "code_cultu" in geojson_df.columns else "non_bio"
    # if filter_code == "CODE_CULTU":
        # geojson_df = geojson_df.to_crs(epsg=4326)/
    # Get the data category
    data_category = get_data_category()
    print(data_category)
    # export the data to a JSON file
    export_data = prepare_data_for_export()
    df = pd.DataFrame(export_data)
    # Export the DataFrame to an Excel file
    df.to_excel(filename + ".xlsx", index=False)


if __name__ == "__main__":
    main()
