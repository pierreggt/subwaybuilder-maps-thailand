from depot.demand import DemandData

if __name__ == "__main__":
    bkk = DemandData('demand_data.json', 'BKK', bbox=[100.30, 12.63, 101.05, 14.08])

    # Suvarnabhumi Airport (BKK) - Main Passenger Terminal 1 confirmed via
    # aeroway=terminal tag in OSM. 62,902,183 total passengers (2025, AOT).
    # Suvarnabhumi is a significant regional connecting hub but no published
    # O&D/connecting-passenger rate was found despite searching -- using the
    # raw total as-is per explicit instruction (unsourced-estimate route
    # rejected in favor of the raw-total default, same situation as
    # Riyadh/Jeddah).
    bkk.add_points({
        "type": "airport", "name": "Suvarnabhumi Airport",
        "code": "BKK", "location": [100.75057357820762, 13.691743999265956],
        "total_capacity": round(62_902_183 / 365), "pop_size": 150,
        "merge_within": 400, "residential_split": 0.05, "max_distance": 60000
    })

    # Don Mueang Airport (DMK) - split by terminal (Terminal 1 = international,
    # Terminal 2 = domestic), both confirmed via aeroway=terminal tags.
    # 2025 totals: 12,243,429 international / 19,407,387 domestic (AOT).
    bkk.add_points({
        "type": "airport", "name": "Don Mueang Airport - Terminal 1",
        "code": "DMK_T1", "location": [100.6034495340608, 13.920432099431935],
        "total_capacity": round(12_243_429 / 365), "pop_size": 150,
        "merge_within": 300, "residential_split": 0.05, "max_distance": 60000
    })
    bkk.add_points({
        "type": "airport", "name": "Don Mueang Airport - Terminal 2",
        "code": "DMK_T2", "location": [100.60165551690544, 13.917573938703022],
        "total_capacity": round(19_407_387 / 365), "pop_size": 150,
        "merge_within": 300, "residential_split": 0.05, "max_distance": 60000
    })

    # U-Tapao Rayong-Pattaya International Airport (UTP) - small
    # regional/charter airport, terminal building confirmed via
    # aeroway=terminal tag. 369,610 passengers (2025, operator figure).
    bkk.add_points({
        "type": "airport", "name": "U-Tapao International Airport",
        "code": "UTP", "location": [100.99807670438409, 12.675989682659488],
        "total_capacity": round(369_610 / 365), "pop_size": 100,
        "merge_within": 300, "residential_split": 0.05, "max_distance": 40000
    })

    # Chulalongkorn University - main campus confirmed via OSM polygon.
    # 37,626 total students (Wikipedia, most detailed breakdown found:
    # 26,202 undergrad + 8,029 postgrad + 2,627 doctoral).
    bkk.add_points({
        "type": "university", "name": "Chulalongkorn University",
        "code": "CHULA", "location": [100.53005210064356, 13.7386404001513],
        "total_capacity": 37_626, "pop_size": 150, "merge_within": 200,
        "residential_split": 0.1, "max_distance": 40000
    })

    # King Chulalongkorn Memorial Hospital - main building confirmed via
    # OSM polygon. 1,435 beds.
    bkk.add_points({
        "type": "hospital", "name": "King Chulalongkorn Memorial Hospital",
        "code": "KCMH", "location": [100.5358302922315, 13.732810204156266],
        "total_capacity": 1_435 * 5, "pop_size": 100, "merge_within": 150
    })

    # Mahidol University - main (Salaya) campus confirmed via OSM polygon.
    # 32,675 students (official Mahidol Quick Facts 2025, most authoritative
    # source found; international rankings report a lower ~29,700-29,900).
    bkk.add_points({
        "type": "university", "name": "Mahidol University",
        "code": "MAHIDOL", "location": [100.32180010002179, 13.794374724217198],
        "total_capacity": 32_675, "pop_size": 150, "merge_within": 200,
        "residential_split": 0.1, "max_distance": 40000
    })

    # Siriraj Hospital (Faculty of Medicine Siriraj Hospital, Mahidol
    # University) - main building confirmed via OSM polygon. 2,145 beds.
    bkk.add_points({
        "type": "hospital", "name": "Siriraj Hospital",
        "code": "SIRIRAJ", "location": [100.48541485155692, 13.757790935908083],
        "total_capacity": 2_145 * 5, "pop_size": 100, "merge_within": 150
    })

    # Ramathibodi Hospital (Faculty of Medicine Ramathibodi Hospital,
    # Mahidol University) - main building confirmed via OSM polygon.
    # 1,023 beds.
    bkk.add_points({
        "type": "hospital", "name": "Ramathibodi Hospital",
        "code": "RAMA", "location": [100.52644274324808, 13.767266948744101],
        "total_capacity": 1_023 * 5, "pop_size": 100, "merge_within": 150
    })

    # Bangkok Hospital Pattaya - private hospital, main building confirmed
    # via OSM polygon (โรงพยาบาลกรุงเทพพัทยา). 300 beds.
    bkk.add_points({
        "type": "hospital", "name": "Bangkok Hospital Pattaya",
        "code": "BHP", "location": [100.90545656924277, 12.953845681006642],
        "total_capacity": 300 * 5, "pop_size": 100, "merge_within": 150
    })

    bkk.save('demand_data.json')
    print("Points speciaux ajoutes.")
