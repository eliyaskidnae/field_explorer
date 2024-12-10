#!/usr/bin/env python3

from flask import Flask, request, jsonify, render_template
import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from filter import *
import os
import click

app = Flask(__name__)
# Default filename
default_filename = "RPG_2-2__SHP_LAMB93_R84_2023-01-01/PARCELLES_GRAPHIQUES.shp"


@click.command()
@click.option(
    "--filepath", default=default_filename, help="Path of the shapefile to load"
)
def get_filename(filepath):
    print("Filepath:", filepath)
    return filepath


# Load GeoJSON data into a Pandas DataFrame when the application starts
def load_geojson_to_dataframe(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    features = data["features"]
    properties = [feature["properties"] for feature in features]
    geometry = [feature["geometry"] for feature in features]
    df = pd.DataFrame(properties)
    df["geometry"] = geometry
    print("number of rows: ", df.shape[0])
    return df


@app.route("/")
def index():
    return render_template("green.html")


@app.route("/data", methods=["GET"])
def get_data():
    # Read the JSON file and send its content as the response
    json_filename = f"{os.path.splitext(filename)[0]}.json"
    main(geojson_df, json_filename, column_name=filter_code)
    with open(json_filename, "r") as f:
        code_cultu_data = json.load(f)
        print("filname", filename)

    response = {"data_file_name": filename, "code_cultu_data": code_cultu_data}
    return jsonify(response)


@app.route("/filter", methods=["POST"])
def filter_data():
    code_cultu = request.form.get("codeCultu")
    surface_ha_min = request.form.get("surfaceHa_min")
    surface_ha_max = request.form.get("surfaceHa_max")
    try:
        surface_ha_min = float(surface_ha_min) if surface_ha_min else None
        surface_ha_max = float(surface_ha_max) if surface_ha_max else None

        filter_surface = (
            "surface_ha" if "surface_ha" in geojson_df.columns else "SURF_PARC"
        )
        filtered_df = geojson_df[
            (geojson_df[filter_code] == code_cultu)
            & (
                (surface_ha_min is None)
                | (geojson_df[filter_surface] >= surface_ha_min)
            )
            & (
                (surface_ha_max is None)
                | (geojson_df[filter_surface] <= surface_ha_max)
            )
        ]

        # Sort the filtered DataFrame
        filtered_df.sort_values(by=filter_surface, ascending=False, inplace=True)

        # Calculate the required statistics
        total_features = len(filtered_df)
        features_lt_1 = len(filtered_df[filtered_df[filter_surface] < 1])
        features_1_to_3 = len(
            filtered_df[
                (filtered_df[filter_surface] >= 1) & (filtered_df[filter_surface] < 3)
            ]
        )
        features_3_to_8 = len(
            filtered_df[
                (filtered_df[filter_surface] >= 3) & (filtered_df[filter_surface] < 8)
            ]
        )
        features_gt_8 = len(filtered_df[filtered_df[filter_surface] >= 8])

        # Convert the filtered DataFrame to JSON
        filtered_features = filtered_df.head(30).to_json()

        # Create the response dictionary
        response = {
            "total_features": total_features,
            "features_lt_1": features_lt_1,
            "features_1_to_3": features_1_to_3,
            "features_3_to_8": features_3_to_8,
            "features_gt_8": features_gt_8,
            "filtered_features": json.loads(filtered_features),
            "all_features": len(geojson_df),
            "data_file_name": filename,
        }

        return jsonify(response)
    except ValueError:
        return jsonify({"error": "Invalid input for surface area."})


if __name__ == "__main__":
    filename = get_filename(standalone_mode=False)
    geojson_df = gpd.read_file(filename)
    filter_code = "code_cultu" if "code_cultu" in geojson_df.columns else "CODE_CULTU"
    if filter_code == "CODE_CULTU":
        geojson_df = geojson_df.to_crs(epsg=4326)
    app.run(debug=True)
