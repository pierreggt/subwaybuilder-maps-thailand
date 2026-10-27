import json

MULTIPLIER = 1.5

d = json.load(open('demand_data.json'))
for p in d['pops']:
    if p['drivingDistance'] >= 3000:
        p['drivingSeconds'] = round(p['drivingSeconds'] * MULTIPLIER)

json.dump(d, open('demand_data.json', 'w'))
print("Traffic simulated.")
