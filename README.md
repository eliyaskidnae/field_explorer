# Field Explorer

### Prerequisites

Make sure you have the following packages installed:

- Flask
- Geopandas
- Pandas

You can install these packages using pip:

```sh
pip install Flask geopandas pandas
```
### Data file setup
Download the rpg-bio-2022.zip file containing the necessary shapefile data.

Unzip the rpg-bio-2022.zip file.
Ensure that the following files are inside the rpg-bio-2022-national folder:
- rpg-bio-2022-national.shp
- rpg-bio-2022-national.prj
- rpg-bio-2022-national.dbf
- rpg-bio-2022-national.cpg
- rpg-bio-2022-national.qix

Additional Files 
pleae put RPG_2-2__GPKG_LAMB93_FXX_2023-01-01/PARCELLES_GRAPHIQUES.gpkg file in your project and run the code as follow
### Running the Application

```sh
#run the script to start the web app
python3 app.py  --filepath rpg-bio-2022-national/rpg-bio-2022-national.shp
python3 app.py  --filepath RPG_2-2__GPKG_LAMB93_FXX_2023-01-01/PARCELLES_GRAPHIQUES.gpkg

#open in browser
http://127.0.0.1:5000/
```