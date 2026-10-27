from depot.maps import MapGen

if __name__ == "__main__":
    mg = MapGen(
        city="CNX",
        bbox=[98.88, 18.70, 99.07, 18.87],
        osmpbf="cnx.osm.pbf",
        outputdir="output",
        RAM=4,
        verb=True,
    )
    mg.run_all()
    print("RUN_ALL OK")
