from depot.demand import DemandData

if __name__ == "__main__":
    bkl = DemandData('demand_data.json', 'BKL', bbox=[100.30, 13.45, 100.78, 14.08])
    bkl.calculate_routes(routing_method="osrm", max_workers=30, osrm_port=5003)
    bkl.save('demand_data.json')
    print("Routes calculees.")
