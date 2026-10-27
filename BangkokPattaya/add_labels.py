from depot.maps import MapGen

if __name__ == "__main__":
    mg = MapGen(
        city="BKK",
        bbox=[100.30, 12.63, 101.05, 14.08],
        osmpbf="bkk.osm.pbf",
        outputdir="output",
        buildings_geojson="output/BKK/buildings_cleaned.json",
        RAM=10,
        verb=True,
        cities=['city', 'town'],
        suburbs=['suburb', 'village'],
        neighborhoods=['neighbourhood', 'quarter', 'hamlet', 'locality'],
    )
    mg.add_labels()
    print("LABELS OK")
