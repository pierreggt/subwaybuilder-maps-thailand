from depot.demand import DemandData

if __name__ == "__main__":
    bkk = DemandData('demand_data.json', 'BKK', bbox=[100.30, 12.63, 101.05, 14.08])
    bkk.calculate_routes(routing_method="osrm", max_workers=30, osrm_port=5002)
    bkk.save('demand_data.json')
    print("Routes calculees.")
