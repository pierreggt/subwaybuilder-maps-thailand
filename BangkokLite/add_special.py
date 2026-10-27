from depot.demand import DemandData

if __name__ == "__main__":
    bkl = DemandData('demand_data.json', 'BKL', bbox=[100.30, 13.45, 100.78, 14.08])

    bkl.add_points({
        "type": "airport", "name": "Suvarnabhumi Airport",
        "code": "BKK", "location": [100.75057357820762, 13.691743999265956],
        "total_capacity": round(62_902_183 / 365), "pop_size": 150,
        "merge_within": 400, "residential_split": 0.05, "max_distance": 60000
    })

    bkl.add_points({
        "type": "airport", "name": "Don Mueang Airport - Terminal 1",
        "code": "DMK_T1", "location": [100.6034495340608, 13.920432099431935],
        "total_capacity": round(12_243_429 / 365), "pop_size": 150,
        "merge_within": 300, "residential_split": 0.05, "max_distance": 60000
    })
    bkl.add_points({
        "type": "airport", "name": "Don Mueang Airport - Terminal 2",
        "code": "DMK_T2", "location": [100.60165551690544, 13.917573938703022],
        "total_capacity": round(19_407_387 / 365), "pop_size": 150,
        "merge_within": 300, "residential_split": 0.05, "max_distance": 60000
    })

    bkl.add_points({
        "type": "university", "name": "Chulalongkorn University",
        "code": "CHULA", "location": [100.53005210064356, 13.7386404001513],
        "total_capacity": 37_626, "pop_size": 150, "merge_within": 200,
        "residential_split": 0.1, "max_distance": 40000
    })
    bkl.add_points({
        "type": "hospital", "name": "King Chulalongkorn Memorial Hospital",
        "code": "KCMH", "location": [100.5358302922315, 13.732810204156266],
        "total_capacity": 1_435 * 5, "pop_size": 100, "merge_within": 150
    })

    bkl.add_points({
        "type": "university", "name": "Mahidol University",
        "code": "MAHIDOL", "location": [100.32180010002179, 13.794374724217198],
        "total_capacity": 32_675, "pop_size": 150, "merge_within": 200,
        "residential_split": 0.1, "max_distance": 40000
    })
    bkl.add_points({
        "type": "hospital", "name": "Siriraj Hospital",
        "code": "SIRIRAJ", "location": [100.48541485155692, 13.757790935908083],
        "total_capacity": 2_145 * 5, "pop_size": 100, "merge_within": 150
    })
    bkl.add_points({
        "type": "hospital", "name": "Ramathibodi Hospital",
        "code": "RAMA", "location": [100.52644274324808, 13.767266948744101],
        "total_capacity": 1_023 * 5, "pop_size": 100, "merge_within": 150
    })

    bkl.save('demand_data.json')
    print("Points speciaux ajoutes.")
