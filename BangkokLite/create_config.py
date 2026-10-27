from depot.demand import DemandData

if __name__ == "__main__":
    bkl = DemandData('demand_data.json', 'BKL', bbox=[100.30, 13.45, 100.78, 14.08])
    bkl.create_config(
        name="Bangkok (Lite)",
        description="A lighter-weight map of core Bangkok, Thailand, covering Don Mueang and Suvarnabhumi airports and the existing BTS/MRT network. Optimized for lower-end computers: smaller area, fewer buildings, and larger demand groupings than the full Bangkok-Pattaya map.",
        creator="pierreggt",
        version="1.0.0",
        country="TH",
        initial_view_state=[100.53, 13.75, 11, 0],
    )
    print("config.json cree")
