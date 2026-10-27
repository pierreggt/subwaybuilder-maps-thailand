from depot.maps import MapGen

if __name__ == "__main__":
    mg = MapGen(
        city="CNX",
        bbox=[98.88, 18.70, 99.07, 18.87],
        osmpbf="cnx.osm.pbf",
        outputdir="output",
        buildings_geojson="output/CNX/buildings_cleaned.json",
        RAM=4,
        verb=True,
        cities=['city', 'town'],
        suburbs=['suburb', 'village'],
        neighborhoods=['neighbourhood', 'quarter', 'hamlet', 'locality'],
    )
    mg.add_labels()
    print("LABELS OK")
