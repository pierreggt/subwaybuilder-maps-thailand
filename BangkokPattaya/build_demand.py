import json
import math
import numpy as np
from shapely.geometry import shape, Point
from shapely.prepared import prep

FINE_GRID_SIZE = 0.0025  # ~280m
DISTRICT_CELL = 0.027  # ~3km, matches synthetic_grid.geojson
MIN_DIST_KM = 3.0
POP_SIZE = 150
EXPONENT = 1.6
MAX_DISTANCE_M = 40000
EMPLOYMENT_RATE = 0.45

CODE = "BKK"
BBOX = [100.30, 12.63, 101.05, 14.08]
LON_MIN, LAT_MIN, LON_MAX, LAT_MAX = BBOX

print("Loading districts (synthetic grid, population already computed)...")
districts = json.load(open("districts.geojson"))
ncols = int(round((LON_MAX - LON_MIN) / DISTRICT_CELL)) + 1
district_pop = {}
for f in districts["features"]:
    district_pop[f["properties"]["name"]] = f["properties"]["population"]


def district_key(lon, lat):
    gx = int((lon - LON_MIN) / DISTRICT_CELL)
    gy = int((lat - LAT_MIN) / DISTRICT_CELL)
    return f"SYN_{gx}_{gy}"


print("Loading airport exclusion polygons...")
airport_polys = []
for fn in ["suv_check.geojson", "dmk_aerodrome.geojson", "utp_check.geojson"]:
    try:
        fc = json.load(open(fn))
    except FileNotFoundError:
        continue
    for f in fc["features"]:
        if f["properties"].get("aeroway") == "aerodrome":
            airport_polys.append(prep(shape(f["geometry"])))

# Also load the actual aerodrome polygons explicitly (suv/utp searches above
# were building-level, not aerodrome-level -- fetch aerodrome polygons fresh)
import subprocess
subprocess.run([
    "ogr2ogr", "-f", "GeoJSON", "all_aerodromes.geojson", "bkk.osm.pbf",
    "multipolygons", "-where", "aeroway='aerodrome'"
], check=True)
fc = json.load(open("all_aerodromes.geojson"))
airport_polys = [prep(shape(f["geometry"])) for f in fc["features"]]
print(f"{len(airport_polys)} airport polygons loaded for exclusion")


def in_any_airport(lon, lat):
    pt = Point(lon, lat)
    for poly in airport_polys:
        if poly.contains(pt):
            return True
    return False


print("Loading buildings index...")
bidx = json.load(open("output/BKK/buildings_index.json"))
buildings = bidx["buildings"]
print(f"{len(buildings)} buildings")

print("Computing building centroids/areas (vectorized)...")
n = len(buildings)
cx = np.empty(n)
cy = np.empty(n)
floors = np.empty(n)
area = np.empty(n)

for i, b in enumerate(buildings):
    bb = b["b"]
    cx[i] = (bb[0] + bb[2]) / 2
    cy[i] = (bb[1] + bb[3]) / 2
    floors[i] = max(b.get("f", 1), 1)
    # shoelace on first ring only, vectorized per-building is fine (3.3M is ok with numpy below via bbox approx)

# Area via bbox approximation is too crude; compute real shoelace but with a
# fast pure-python loop restricted to coordinate arrays (still O(n) overall,
# not O(n^2) -- the earlier slowness in the Chiang Mai script was the
# per-building STRtree polygon query, not the shoelace calc itself).
def shoelace(coords):
    arr = np.array(coords)
    x = arr[:, 0]
    y = arr[:, 1]
    return abs(np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])) / 2.0

for i, b in enumerate(buildings):
    try:
        area[i] = shoelace(b["p"][0])
    except Exception:
        area[i] = 0.0
    if i % 500000 == 0:
        print(f"  area calc {i}/{n}")

cap = np.percentile(area[area > 0], 95)
area_capped = np.minimum(area, cap)
weight = area_capped * floors
print("area cap (deg^2):", cap)

print("Assigning buildings to district + fine grid cells (vectorized)...")
gx_district = ((cx - LON_MIN) / DISTRICT_CELL).astype(int)
gy_district = ((cy - LAT_MIN) / DISTRICT_CELL).astype(int)
gx_fine = (cx / FINE_GRID_SIZE).astype(int)
gy_fine = (cy / FINE_GRID_SIZE).astype(int)

print("Checking airport exclusion (only for buildings near airports, via bbox prefilter)...")
airport_bboxes = []
for fn_feats in [json.load(open("all_aerodromes.geojson"))["features"]]:
    for f in fn_feats:
        airport_bboxes.append(shape(f["geometry"]).bounds)

near_airport_mask = np.zeros(n, dtype=bool)
for (minx, miny, maxx, maxy) in airport_bboxes:
    near_airport_mask |= (cx >= minx) & (cx <= maxx) & (cy >= miny) & (cy <= maxy)

excluded = np.zeros(n, dtype=bool)
near_idxs = np.where(near_airport_mask)[0]
print(f"{len(near_idxs)} buildings near an airport bbox, checking exact polygon...")
for idx in near_idxs:
    if in_any_airport(cx[idx], cy[idx]):
        excluded[idx] = True
print(f"{excluded.sum()} buildings excluded (inside airport polygon)")

res_weight = {}
for i in range(n):
    if excluded[i] or weight[i] <= 0:
        continue
    dkey = f"SYN_{gx_district[i]}_{gy_district[i]}"
    key = (dkey, gx_fine[i], gy_fine[i])
    res_weight[key] = res_weight.get(key, 0.0) + weight[i]
    if i % 1000000 == 0 and i > 0:
        print(f"  residential assign {i}/{n}")

print(f"{len(res_weight)} occupied residential grid cells")

print("Loading POI economic points...")
poi = json.load(open("poi_points.geojson"))
job_weight = {}
for f in poi["features"]:
    geom = f["geometry"]
    if geom["type"] != "Point":
        continue
    plon, plat = geom["coordinates"]
    dkey = f"SYN_{int((plon - LON_MIN) / DISTRICT_CELL)}_{int((plat - LAT_MIN) / DISTRICT_CELL)}"
    gx = int(plon / FINE_GRID_SIZE)
    gy = int(plat / FINE_GRID_SIZE)
    key = (dkey, gx, gy)
    job_weight[key] = job_weight.get(key, 0.0) + 1.0

print(f"{len(job_weight)} occupied job grid cells")

points = []
all_cells = {}


def cell_center(gx, gy):
    return (gx + 0.5) * FINE_GRID_SIZE, (gy + 0.5) * FINE_GRID_SIZE


res_by_district = {}
for (dname, gx, gy), w in res_weight.items():
    res_by_district.setdefault(dname, []).append(((gx, gy), w))

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
        all_cells.setdefault(key, {"residents": 0, "jobs": 0, "lon": lon, "lat": lat})
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
        all_cells.setdefault(key, {"residents": 0, "jobs": 0, "lon": lon, "lat": lat})
        all_cells[key]["jobs"] += jobs

cell_list = list(all_cells.items())
print(f"{len(cell_list)} total cells (residential and/or job)")
total_residents = sum(c["residents"] for _, c in cell_list)
total_jobs = sum(c["jobs"] for _, c in cell_list)
print(f"total residents={total_residents} total jobs={total_jobs}")

for i, (key, c) in enumerate(cell_list):
    points.append({
        "id": f"P{i}",
        "location": [c["lon"], c["lat"]],
        "jobs": 0,
        "residents": 0,
        "popIds": [],
    })
    c["pid"] = f"P{i}"

lons = np.array([c["lon"] for _, c in cell_list])
lats = np.array([c["lat"] for _, c in cell_list])
jobs_arr = np.array([c["jobs"] for _, c in cell_list], dtype=float)

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
    dx = dlon * 111320 * math.cos(math.radians(olat))
    dy = dlat * 111320
    dist_m = np.sqrt(dx ** 2 + dy ** 2)
    with np.errstate(divide="ignore"):
        weights = jobs_arr[job_cell_idxs] / np.power(np.maximum(dist_m, 1), EXPONENT)
    weights[dist_m > MAX_DISTANCE_M] /= 10
    if weights.sum() <= 0:
        continue
    far_mask = dist_m >= MIN_DIST_KM * 1000
    if far_mask.any():
        far_weights = weights * far_mask
        probs = far_weights / far_weights.sum()
    else:
        probs = weights / weights.sum()

    while remaining > 0:
        size = min(POP_SIZE, remaining)
        remaining -= size
        ji = rng.choice(len(job_cell_idxs), p=probs)
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

    if origin_i % 50000 == 0:
        print(f"  gravity assign {origin_i}/{len(cell_list)}")

print(f"{len(pops)} pops generated")

demand_data = {"points": points, "pops": pops}
json.dump(demand_data, open("demand_data_base.json", "w"))
print("Saved demand_data_base.json")
print("Total residents in points:", sum(p["residents"] for p in points))
print("Total jobs in points:", sum(p["jobs"] for p in points))
