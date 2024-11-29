from flask import Flask, request, jsonify, render_template
import json
import geopandas as gpd
import pandas as pd

app = Flask(__name__)


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


geojson_df = gpd.read_file("rpg-bio-2022-national/rpg-bio-2022-national.shp")


@app.route("/")
def index():
    return render_template("green.html")


@app.route("/data", methods=["GET"])
def get_data():
    # Read the JSON file and send its content as the response
    with open("unique_code_cultu.json", "r") as f:
        code_cultu_data = json.load(f)
    return jsonify(code_cultu_data)


@app.route("/filter", methods=["POST"])
def filter_data():
    code_cultu = request.form.get("codeCultu")
    surface_ha_min = request.form.get("surfaceHa_min")
    surface_ha_max = request.form.get("surfaceHa_max")
    try:
        surface_ha_min = float(surface_ha_min) if surface_ha_min else None
        surface_ha_max = float(surface_ha_max) if surface_ha_max else None

        # Filter the DataFrame based on the input criteria
        filtered_df = geojson_df[
            (geojson_df["lbl_cultur"] == code_cultu)
            & ((surface_ha_min is None) | (geojson_df["surface_ha"] >= surface_ha_min))
            & ((surface_ha_max is None) | (geojson_df["surface_ha"] <= surface_ha_max))
        ]

        # Sort the filtered DataFrame
        filtered_df.sort_values(by="surface_ha", ascending=False, inplace=True)

        # Calculate the required statistics
        total_features = len(filtered_df)
        features_lt_1 = len(filtered_df[filtered_df["surface_ha"] < 1])
        features_1_to_3 = len(
            filtered_df[
                (filtered_df["surface_ha"] >= 1) & (filtered_df["surface_ha"] < 3)
            ]
        )
        features_3_to_8 = len(
            filtered_df[
                (filtered_df["surface_ha"] >= 3) & (filtered_df["surface_ha"] < 8)
            ]
        )
        features_gt_8 = len(filtered_df[filtered_df["surface_ha"] >= 8])

        # Convert the filtered DataFrame to JSON
        filtered_features = filtered_df.head(1000).to_json()

        # Create the response dictionary
        response = {
            "total_features": total_features,
            "features_lt_1": features_lt_1,
            "features_1_to_3": features_1_to_3,
            "features_3_to_8": features_3_to_8,
            "features_gt_8": features_gt_8,
            "filtered_features": json.loads(filtered_features),
            "all_features": len(geojson_df),
        }

        return jsonify(response)
    except ValueError:
        return jsonify({"error": "Invalid input for surface area."})


if __name__ == "__main__":
    app.run(debug=True)
