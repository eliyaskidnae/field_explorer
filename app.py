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

        filtered_df = geojson_df[
            (geojson_df["code_cultu"] == code_cultu)
            & ((surface_ha_min is None) | (geojson_df["surface_ha"] >= surface_ha_min))
            & ((surface_ha_max is None) | (geojson_df["surface_ha"] <= surface_ha_max))
        ]
        filtered_df.sort_values(by="surface_ha", ascending=False, inplace=True)
        filtered_features = filtered_df.head(1000).to_json()

        return jsonify(json.loads(filtered_features))
    except ValueError:
        return jsonify({"error": "Invalid input for surface area."})


if __name__ == "__main__":
    app.run(debug=True)
