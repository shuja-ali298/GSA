
"""
Run a minimal geospatial workflow using GeoPandas and Folium.
- Loads Natural Earth countries sample
- Reprojects to equal-area CRS to compute area (km^2)
- Saves top 20 by area to CSV
- Exports a static choropleth and a simple interactive map
"""
import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import folium

# ---- Paths ----
ROOT = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(ROOT, "outputs")
FIG_DIR = os.path.join(OUT_DIR, "figures")
MAP_DIR = os.path.join(OUT_DIR, "maps")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(MAP_DIR, exist_ok=True)

# ---- Load sample data ----
world_fp = gpd.datasets.get_path("naturalearth_lowres")
world = gpd.read_file(world_fp)

# Clean a bit: remove Antarctica (huge polygon) and missing pop_est
world = world[world["name"] != "Antarctica"].copy()

# ---- Compute area in an equal-area CRS ----
# World Equal Area (EPSG:6933) is good for global area calcs
world_eq = world.to_crs(6933)
world_eq["area_km2"] = world_eq.geometry.area / 1e6

# ---- Export Top 20 largest countries ----
top20 = world_eq.nlargest(20, "area_km2")[["name", "continent", "area_km2"]]
top20 = top20.sort_values("area_km2", ascending=False).reset_index(drop=True)
top20.to_csv(os.path.join(OUT_DIR, "world_area_top20.csv"), index=False)

# ---- Static choropleth (matplotlib) ----
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(111)
world_eq.plot(column="area_km2", scheme="quantiles", k=5, legend=True, ax=ax, edgecolor="black", linewidth=0.2)
ax.set_title("Country Area (km²) — Equal-Area Projection", pad=10)
ax.set_axis_off()
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "world_area.png"), dpi=180)
plt.close(fig)

# ---- Simple interactive map (Folium) ----
# We'll add centroids with popups for a quick demo
centroids = world.copy()
centroids["centroid"] = centroids.geometry.centroid
centroids_points = centroids.set_geometry("centroid").to_crs(4326)

m = folium.Map(location=[20, 0], zoom_start=2)
for _, row in centroids_points.iterrows():
    name = row["name"]
    continent = row["continent"]
    coords = (row.geometry.y, row.geometry.x)
    folium.CircleMarker(
        location=coords,
        radius=3,
        fill=True,
        popup=f"{name} — {continent}",
    ).add_to(m)

m.save(os.path.join(MAP_DIR, "world_map.html"))

print("Done! Check the outputs/ folder for results.")
