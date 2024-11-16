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


### Running the Application

```sh
#run the script to start the web app
python3 app.py
#open in browser
http://127.0.0.1:5000/
```