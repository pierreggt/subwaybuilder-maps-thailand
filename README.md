# Subway Builder Maps — Thailand (pierreggt)

Source scripts for two Thailand maps: **Chiang Mai** and **Bangkok - Pattaya**.

These maps are **not submitted to the Subway-Builder-Modded registry**. They're distributed as flat data archives for local import directly in Railyard (no mod folder, no auto-update). This repo exists so anyone installing them can read exactly what generated the data before running it.

## Download

Grab the latest zip from [Releases](../../releases) and import it locally in Railyard.

## What's in each folder

- `build.py` — geographic build (OSM extraction, buildings via Overture, roads, PMTiles) using [depot](https://github.com/Subway-Builder-Modded/depot)
- `build_demand.py` — population/employment demand model. No official commuter-flow dataset exists for Thailand, so this uses: real population per grid cell (WorldPop 2020 raster, zonal-aggregated), OSM POI density as an employment proxy, and a gravity model (distance-decay, 3km minimum trip distance enforced with retries) to generate commute flows
- `add_special.py` — airports, universities, hospitals, each verified against real OSM terminal/campus/hospital buildings (never the airport reference point or aerodrome centroid) with sourced passenger/enrollment/bed figures
- `calc_routes_osrm.py` — driving routes via a local OSRM instance on the real OpenStreetMap road network
- `simulate_traffic.py` — traffic multiplier on trips ≥3km
- `create_config.py` / `package.py` — final `config.json` and data packaging
- `*_check.geojson` — the OSM queries used to verify special-point locations (terminal buildings, campus/hospital polygons) before fixing their coordinates

## Methodology notes

- **Population**: WorldPop 2020 gridded population (not an official census grid — Thailand's NSO doesn't publish one), aggregated per ~3km synthetic cell, redistributed to buildings by footprint area × floor count on a ~280m display grid.
- **Employment**: no official commuter matrix exists for Thailand; jobs are estimated from OSM economic POI density (shops, offices, restaurants, banks, etc.) and distributed via the same gravity model as residents.
- **Bangkok - Pattaya**: this is a single fused map despite weak transit justification — the only real rail link between the two is a once-daily conventional train, and the planned high-speed rail link (Don Mueang–Suvarnabhumi–U-Tapao) is stalled with no construction started. Built as one map anyway per the creator's choice; flagged here for transparency.
- **Suvarnabhumi Airport**: uses raw total passenger traffic (62.9M, 2025) as the demand input. No official connecting/transfer-passenger rate is published for this airport, so unlike some other hub airports in this creator's other maps, no O&D correction was applied.
- Both maps have one known cosmetic imperfection: large stretches of shallow coastal water (notably the inner Gulf of Thailand near Samut Prakan on the Bangkok map) render as a flat gray-blue instead of a natural depth gradient, because GEBCO bathymetry data doesn't resolve very shallow intertidal zones well. Accepted as-is.

## License

GNU General Public License v3.0.

## Credits

Maps authored by pierreggt. Built with [depot](https://github.com/Subway-Builder-Modded/depot). Data: OpenStreetMap, Overture Maps Foundation, WorldPop.
