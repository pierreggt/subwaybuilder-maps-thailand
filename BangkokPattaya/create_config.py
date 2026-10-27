from depot.demand import DemandData

if __name__ == "__main__":
    bkk = DemandData('demand_data.json', 'BKK', bbox=[100.30, 12.63, 101.05, 14.08])
    bkk.create_config(
        name="Bangkok - Pattaya",
        description="Map of the Bangkok metropolitan area and Pattaya, Thailand, from Don Mueang and Suvarnabhumi airports through central Bangkok's BTS/MRT network to Pattaya and U-Tapao airport.",
        creator="pierreggt",
        version="1.0.0",
        country="TH",
        initial_view_state=[100.60, 13.55, 9, 0],
    )
    print("config.json cree")
