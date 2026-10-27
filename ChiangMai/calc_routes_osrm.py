from depot.demand import DemandData

if __name__ == "__main__":
    cnx = DemandData('demand_data.json', 'CNX', bbox=[98.88, 18.70, 99.07, 18.87])
    cnx.calculate_routes(routing_method="osrm", max_workers=30, osrm_port=5001)
    cnx.save('demand_data.json')
    print("Routes calculees.")
