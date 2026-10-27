from depot.maps import MapGen

if __name__ == "__main__":
    mg = MapGen(
        city="BKK",
        bbox=[100.30, 12.63, 101.05, 14.08],
        osmpbf="bkk.osm.pbf",
        outputdir="output",
        RAM=10,
        verb=True,
    )
    mg.run_all()
    print("RUN_ALL OK")
