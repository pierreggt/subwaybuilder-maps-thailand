import sys, os, gzip, shutil
sys.path.insert(0, '../shared-resources')
from gen_mod_files import generate

CODE = "BKL"
MODDIR = "../game-mods/BangkokLite"
os.makedirs(MODDIR, exist_ok=True)
os.makedirs(f"{MODDIR}/data/{CODE}", exist_ok=True)

generate(
    outdir=MODDIR, code=CODE, mod_id="bangkoklite",
    name_en="Bangkok (Lite)", name_fr="Bangkok (Allegee)",
    desc_en="A lighter-weight map of core Bangkok, Thailand, covering Don Mueang and Suvarnabhumi airports and the existing BTS/MRT network. Optimized for lower-end computers.",
    desc_fr="Une carte allegee du coeur de Bangkok, Thailande, couvrant les aeroports de Don Mueang et Suvarnabhumi et le reseau BTS/MRT existant. Optimisee pour les ordinateurs moins puissants.",
    notif_extra_en="", notif_extra_fr="",
    population=18438927, lat=13.75, lon=100.53, zoom=12
)

idx_path = f"{MODDIR}/index.js"
with open(idx_path) as f:
    content = f.read()
content = content.replace(
    f"api.cities.registerTab({{ id: 'france-{CODE.lower()}', label: 'France', cityCodes: ['{CODE}'] }});",
    f"api.cities.registerTab({{ id: 'thailand-{CODE.lower()}', label: 'Thailand', cityCodes: ['{CODE}'] }});"
)
content = content.replace("127.0.0.1:8080", "127.0.0.1:8097")
with open(idx_path, 'w') as f:
    f.write(content)

for fname in ["run_mac-linux.sh", "run_windows.bat"]:
    fpath = f"{MODDIR}/{fname}"
    with open(fpath) as f:
        c = f.read()
    c = c.replace("--port 8080", "--port 8097").replace("port 8080", "port 8097")
    with open(fpath, 'w') as f:
        f.write(c)

shutil.copy(f"output/{CODE}/{CODE}.pmtiles", f"{MODDIR}/{CODE}.pmtiles")
shutil.copy(f"output/{CODE}/{CODE}_foundations.pmtiles", f"{MODDIR}/{CODE}_foundations.pmtiles")

def gz_copy(src, dst):
    with open(src, 'rb') as fin, gzip.open(dst, 'wb') as fout:
        shutil.copyfileobj(fin, fout)

datadir = f"{MODDIR}/data/{CODE}"
gz_copy(f"{CODE}/demand_data.json", f"{datadir}/demand_data.json.gz")
gz_copy(f"output/{CODE}/roads.geojson", f"{datadir}/roads.geojson.gz")
gz_copy(f"output/{CODE}/runways_taxiways.geojson", f"{datadir}/runways_taxiways.geojson.gz")
shutil.copy(f"output/{CODE}/ocean_depth_index.json.gz", f"{datadir}/ocean_depth_index.json.gz")
shutil.copy(f"output/{CODE}/ocean_depth_index_contours.json.gz", f"{datadir}/ocean_depth_index_contours.json.gz")
shutil.copy(f"output/{CODE}/buildings_index.bin.gz", f"{datadir}/buildings_index.bin.gz")
shutil.copy(f"{CODE}/config.json", f"{datadir}/config.json")

print("Mod folder pret:", MODDIR)

FLAT = f"final_{CODE}"
os.makedirs(FLAT, exist_ok=True)
shutil.copy(f"{CODE}/config.json", f"{FLAT}/config.json")
shutil.copy(f"{datadir}/demand_data.json.gz", f"{FLAT}/demand_data.json.gz")
shutil.copy(f"{datadir}/roads.geojson.gz", f"{FLAT}/roads.geojson.gz")
shutil.copy(f"{datadir}/runways_taxiways.geojson.gz", f"{FLAT}/runways_taxiways.geojson.gz")
shutil.copy(f"{datadir}/buildings_index.bin.gz", f"{FLAT}/buildings_index.bin.gz")
shutil.copy(f"{datadir}/ocean_depth_index.json.gz", f"{FLAT}/ocean_depth_index.json.gz")
shutil.copy(f"{datadir}/ocean_depth_index_contours.json.gz", f"{FLAT}/ocean_depth_index_contours.json.gz")
shutil.copy(f"output/{CODE}/{CODE}.pmtiles", f"{FLAT}/{CODE}.pmtiles")

print("Zip a plat pret dans:", FLAT)
