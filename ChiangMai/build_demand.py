import json
import math
import numpy as np
from shapely.geometry import shape, Point, box
from shapely.prepared import prep
from shapely.strtree import STRtree

airport_fc = json.load(open("airport_check.geojson"))
AIRPORT_POLY = prep(shape(airport_fc["features"][0]["geometry"]))

FINE_GRID_SIZE = 0.0025  # ~280m at this latitude
MIN_DIST_KM = 3.0
MAX_RETRIES = 15
POP_SIZE = 100
EXPONENT = 1.6
MAX_DISTANCE_M = 25000
EMPLOYMENT_RATE = 0.45  # share of population assumed employed, distributed by POI density

CODE = "CNX"


def haversine(lon1, lat1, lon2, lat2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def shoelace_area(coords):
    n = len(coords)
    area = 0.0
    for i in range(n - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


print("Loading districts...")
districts = json.load(open("districts.geojson"))
district_geoms = []
district_pop = {}
for f in districts["features"]:
    name = f["properties"]["name"]
    geom = shape(f["geometry"])
    district_geoms.append((name, geom, prep(geom)))
    district_pop[name] = f["properties"]["population"]

print("Loading buildings index...")
bidx = json.load(open("output/CNX/buildings_index.json"))
buildings = bidx["buildings"]
print(f"{len(buildings)} buildings")

# Cap extreme building areas at the 95th percentile (avoid single buildings hoarding population)
areas = []
for b in buildings:
    try:
        a = shoelace_area(b["p"][0])
    except Exception:
        a = 0
    areas.append(a)
areas = np.array(areas)
cap = np.percentile(areas[areas > 0], 95)
print("area cap (deg^2):", cap)

print("Assigning buildings to grid cells + districts...")
# Build spatial index for district lookup
geoms_only = [g for _, g, _ in district_geoms]
tree = STRtree(geoms_only)

res_weight = {}  # (district, gx, gy) -> weight
for b, a in zip(buildings, areas):
    if a <= 0:
        continue
    a = min(a, cap)
    cx = (b["b"][0] + b["b"][2]) / 2
    cy = (b["b"][1] + b["b"][3]) / 2
    pt = Point(cx, cy)
    idxs = tree.query(pt)
    found = None
    for i in idxs:
        name, geom, prepared = district_geoms[i]
        if prepared.contains(pt):
            found = name
            break
    if found is None:
        continue
    gx = int(cx / FINE_GRID_SIZE)
    gy = int(cy / FINE_GRID_SIZE)
    # Exclude by grid-CELL center, not just the source building's centroid --
    # a building just outside the airport polygon can still round into a cell
    # whose center falls inside it (documented Baghdad pitfall).
    cell_cx = (gx + 0.5) * FINE_GRID_SIZE
    cell_cy = (gy + 0.5) * FINE_GRID_SIZE
    if AIRPORT_POLY.contains(Point(cell_cx, cell_cy)):
        continue
    key = (found, gx, gy)
    weight = a * max(b.get("f", 1), 1)
    res_weight[key] = res_weight.get(key, 0.0) + weight

print(f"{len(res_weight)} occupied residential grid cells")

print("Loading POI economic points...")
poi = json.load(open("poi_points.geojson"))
job_weight = {}
for f in poi["features"]:
    geom = f["geometry"]
    if geom["type"] != "Point":
        continue
    cx, cy = geom["coordinates"]
    pt = Point(cx, cy)
    idxs = tree.query(pt)
    found = None
    for i in idxs:
        name, g, prepared = district_geoms[i]
        if prepared.contains(pt):
            found = name
            break
    if found is None:
        continue
    gx = int(cx / FINE_GRID_SIZE)
    gy = int(cy / FINE_GRID_SIZE)
    key = (found, gx, gy)
    job_weight[key] = job_weight.get(key, 0.0) + 1.0

print(f"{len(job_weight)} occupied job grid cells")

# Build points: residents scaled to match real district population; jobs scaled to EMPLOYMENT_RATE * district pop
points = []
point_id_of_cell = {}


def cell_center(gx, gy):
    return (gx + 0.5) * FINE_GRID_SIZE, (gy + 0.5) * FINE_GRID_SIZE


# Normalize residents per district to match real population
res_by_district = {}
for (dname, gx, gy), w in res_weight.items():
    res_by_district.setdefault(dname, []).append(((gx, gy), w))

all_cells = {}  # cell_key(dname,gx,gy) -> {'residents':int,'jobs':int,'lon':..,'lat':..}
for dname, cells in res_by_district.items():
    total_w = sum(w for _, w in cells)
    real_pop = district_pop.get(dname, 0)
    if total_w <= 0 or real_pop <= 0:
        continue
    for (gx, gy), w in cells:
        residents = round(real_pop * w / total_w)
        if residents <= 0:
            continue
        lon, lat = cell_center(gx, gy)
        key = (dname, gx, gy)
        all_cells.setdefault(key, {"residents": 0, "jobs": 0, "lon": lon, "lat": lat, "district": dname})
        all_cells[key]["residents"] = residents

job_by_district = {}
for (dname, gx, gy), w in job_weight.items():
    job_by_district.setdefault(dname, []).append(((gx, gy), w))

for dname, cells in job_by_district.items():
    total_w = sum(w for _, w in cells)
    real_pop = district_pop.get(dname, 0)
    target_jobs = real_pop * EMPLOYMENT_RATE
    if total_w <= 0 or target_jobs <= 0:
        continue
    for (gx, gy), w in cells:
        jobs = round(target_jobs * w / total_w)
        if jobs <= 0:
            continue
        lon, lat = cell_center(gx, gy)
        key = (dname, gx, gy)
        all_cells.setdefault(key, {"residents": 0, "jobs": 0, "lon": lon, "lat": lat, "district": dname})
        all_cells[key]["jobs"] += jobs

cell_list = list(all_cells.items())
print(f"{len(cell_list)} total cells (residential and/or job)")
total_residents = sum(c["residents"] for _, c in cell_list)
total_jobs = sum(c["jobs"] for _, c in cell_list)
print(f"total residents={total_residents} total jobs={total_jobs}")

# Build points array
for i, (key, c) in enumerate(cell_list):
    points.append({
        "id": f"P{i}",
        "location": [c["lon"], c["lat"]],
        "jobs": 0,
        "residents": 0,
        "popIds": [],
    })
    point_id_of_cell[key] = f"P{i}"
    c["pid"] = f"P{i}"

# Gravity model: generate pops from residential cells to job cells
lons = np.array([c["lon"] for _, c in cell_list])
lats = np.array([c["lat"] for _, c in cell_list])
jobs_arr = np.array([c["jobs"] for _, c in cell_list], dtype=float)
pids = [c["pid"] for _, c in cell_list]

pops = []
pop_counter = 0
rng = np.random.default_rng(42)

job_cell_idxs = np.where(jobs_arr > 0)[0]
print(f"{len(job_cell_idxs)} job-bearing cells for gravity assignment")

for origin_i, (key, c) in enumerate(cell_list):
    residents = c["residents"]
    if residents <= 0:
        continue
    remaining = residents
    olon, olat = c["lon"], c["lat"]
    dlon = lons[job_cell_idxs] - olon
    dlat = lats[job_cell_idxs] - olat
    # approx meters
    dx = dlon * 111320 * math.cos(math.radians(olat))
    dy = dlat * 111320
    dist_m = np.sqrt(dx ** 2 + dy ** 2)
    with np.errstate(divide="ignore"):
        weights = jobs_arr[job_cell_idxs] / np.power(np.maximum(dist_m, 1), EXPONENT)
    weights[dist_m > MAX_DISTANCE_M] /= 10
    if weights.sum() <= 0:
        continue
    probs = weights / weights.sum()

    # Mask out cells under MIN_DIST_KM so the gravity draw can't land on a
    # too-close destination in the first place (random retry against the
    # unmasked distribution kept re-landing on the same dominant nearby
    # cell -- 59% of pops ended up under 3km before this fix).
    far_mask = dist_m >= MIN_DIST_KM * 1000
    if far_mask.any():
        far_weights = weights * far_mask
        probs_far = far_weights / far_weights.sum()
    else:
        probs_far = None  # structurally impossible to go far enough; accept close trips

    while remaining > 0:
        size = min(POP_SIZE, remaining)
        remaining -= size
        use_probs = probs_far if probs_far is not None else probs
        ji = rng.choice(len(job_cell_idxs), p=use_probs)
        chosen = job_cell_idxs[ji]
        dest_key, dest_c = cell_list[chosen]
        pop_id = f"pop_{pop_counter}"
        pop_counter += 1
        pops.append({
            "id": pop_id,
            "residenceId": c["pid"],
            "jobId": dest_c["pid"],
            "size": int(size),
            "drivingSeconds": 0,
            "drivingDistance": 0,
        })
        points[origin_i]["residents"] += int(size)
        points[chosen]["jobs"] += int(size)
        points[origin_i]["popIds"].append(pop_id)
        points[chosen]["popIds"].append(pop_id)

print(f"{len(pops)} pops generated")

demand_data = {"points": points, "pops": pops}
json.dump(demand_data, open("demand_data_base.json", "w"))
print("Saved demand_data_base.json")
print("Total residents in points:", sum(p["residents"] for p in points))
print("Total jobs in points:", sum(p["jobs"] for p in points))
