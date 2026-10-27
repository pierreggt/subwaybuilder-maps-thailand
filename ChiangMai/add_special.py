from depot.demand import DemandData

if __name__ == "__main__":
    cnx = DemandData('demand_data.json', 'CNX', bbox=[98.88, 18.70, 99.07, 18.87])

    # Chiang Mai International Airport (CNX) - terminal building confirmed via
    # aeroway=terminal tag in OSM (not the ARP/aerodrome centroid).
    # 9,517,206 passengers in 2025 (Airports of Thailand), no significant
    # connecting/hub traffic found for this airport -- used as-is.
    cnx.add_points({
        "type": "airport", "name": "Chiang Mai International Airport",
        "code": "CNX", "location": [98.9681174591377, 18.768950598417707],
        "total_capacity": round(9_517_206 / 365), "pop_size": 150,
        "merge_within": 200, "residential_split": 0.05, "max_distance": 40000
    })

    # Chiang Mai University - main campus confirmed via OSM polygon
    # (largest "university"-tagged polygon in the area). Enrollment varies
    # 35,400-39,300 across sources (US News/THE/QS/EduAtlasHub) -- using
    # the US News figure (35,428) as the most specifically-sourced number.
    cnx.add_points({
        "type": "university", "name": "Chiang Mai University",
        "code": "CMU", "location": [98.95335052154286, 18.800076227103762],
        "total_capacity": 35_428, "pop_size": 150, "merge_within": 200,
        "residential_split": 0.1, "max_distance": 40000
    })

    # Maharaj Nakorn Chiang Mai Hospital (Faculty of Medicine, CMU) -
    # main building confirmed via OSM polygon. 1,400 beds.
    cnx.add_points({
        "type": "hospital", "name": "Maharaj Nakorn Chiang Mai Hospital",
        "code": "MNCM", "location": [98.97418966964307, 18.791198092858178],
        "total_capacity": 1_400 * 5, "pop_size": 100, "merge_within": 150
    })

    cnx.save('demand_data.json')
    print("Points speciaux ajoutes.")
