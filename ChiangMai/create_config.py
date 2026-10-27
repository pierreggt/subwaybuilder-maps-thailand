from depot.demand import DemandData

if __name__ == "__main__":
    cnx = DemandData('demand_data.json', 'CNX', bbox=[98.88, 18.70, 99.07, 18.87])
    cnx.create_config(
        name="Chiang Mai",
        description="Map of Chiang Mai, Thailand, from Chiang Mai International Airport to the Old City and Chiang Mai University.",
        creator="pierreggt",
        version="1.0.0",
        country="TH",
        initial_view_state=[98.99, 18.79, 12, 0],
    )
    print("config.json cree")
