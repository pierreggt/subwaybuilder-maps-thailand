from depot.maps import MapGen

if __name__ == "__main__":
    mg = MapGen(
        city="BKL",
        bbox=[100.30, 13.45, 100.78, 14.08],
        osmpbf="bkl.osm.pbf",
        outputdir="output",
        buildings_geojson="buildings_filtered.geojson",
        building_index_filter_size=80,
        building_tile_filter_size=80,
        RAM=10,
        verb=True,
        cities=['city', 'town'],
        suburbs=['suburb', 'village'],
        neighborhoods=['neighbourhood', 'quarter', 'hamlet', 'locality'],
    )
    mg.run_all()
    print("RUN_ALL OK")
