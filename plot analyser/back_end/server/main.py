import sys
import os
import math
import json
import logging

# --- FIX: Tkinter Threading Error ---
# This must happen BEFORE any other plotting imports
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

import pyproj
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shapely.geometry import Polygon
from shapely.ops import transform

# ---------------- LOGGING SETUP ---------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("site-analysis")

# ---------------- PATH SETUP ---------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '..')))

# ---------------- IMPORTS ---------------- #
try:
    from site_inteligence_engine.boundary_dimensions import plot_edge_dimensions
    from site_inteligence_engine.roads import (
        fetch_roads_for_plot,
        fetch_all_roads_for_plot,
        road_geometries,
        plot_edges_to_lines,
        detect_frontage
    )
    from environmet_analysis_engine.sunlight import sunlight_analysis
    from environmet_analysis_engine.wind import wind_analysis
    from ploting_engine.draw_context_map import draw_context_map
    from ploting_engine.draw_planning_map import draw_planning_map

    logger.info("✅ All internal modules imported successfully.")
except ImportError as e:
    logger.error(f"❌ Import Error: {e}")
    raise e

# ---------------- FASTAPI APP ---------------- #
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HELPERS ---------------- #
def get_accurate_area_m2(coords):
    poly = Polygon(coords)
    if not poly.is_valid:
        poly = poly.buffer(0)
    project = pyproj.Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True).transform
    projected_poly = transform(project, poly)
    return projected_poly.area

def edge_angle(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    return (math.degrees(math.atan2(dx, dy)) + 360) % 360

def angle_to_cardinal(a):
    if a < 45 or a >= 315: return "North"
    if a < 135: return "East"
    if a < 225: return "South"
    return "West"

# ---------------- API ROUTE ---------------- #
@app.post("/analyze-site")
def analyze_site(geojson: dict):
    logger.info("🚀 Received Request: analyze-site")
    
    try:
        # ---------- 1. Plot geometry & Area ----------
        # Support both FeatureCollection and raw geometry
        if "features" in geojson:
            polygon = geojson["features"][0]["geometry"]["coordinates"][0]
        else:
            polygon = geojson["geometry"]["coordinates"][0]
            
        total_area_m2 = get_accurate_area_m2(polygon)

        # ---------- 2. Plot edges & Roads ----------
        plot_edges = plot_edges_to_lines(polygon)
        osm_roads_main = fetch_roads_for_plot(polygon)
        road_lines_main = road_geometries(osm_roads_main)
        osm_roads_all = fetch_all_roads_for_plot(polygon)
        road_lines_all = road_geometries(osm_roads_all)

        # ---------- 3. Frontage ----------
        frontage = detect_frontage(plot_edges, road_lines_main)
        front_idx = frontage["front_edge_index"]
        
        # Ensure we don't index out of bounds if polygon is not closed
        next_idx = (front_idx + 1) % len(polygon)
        front_angle = edge_angle(polygon[front_idx], polygon[next_idx])

        # ---------- 4. Environmental Analysis ----------
        # Exclude the last redundant point in a closed loop for edge analysis
        edge_data = [{"angle": edge_angle(polygon[i], polygon[i + 1])} for i in range(len(polygon) - 1)]
        latitude = polygon[0][1]
        sunlight = sunlight_analysis(edge_data, latitude)
        wind = wind_analysis(edge_data, latitude)

        # ---------- 5. ZONING ----------
        

        # ---------- 6. Boundary Dimensions ----------
        dimensions = plot_edge_dimensions(polygon)

        # ---------- 7. Draw Images ----------
        context_path = os.path.join(BASE_DIR, "site_context.png")
        planning_path = os.path.join(BASE_DIR, "site_planning.png")
        # We ensure plots are cleared after generation
        draw_context_map(polygon, road_lines_all, save_path=context_path)
        plt.close('all') 
        draw_planning_map(polygon, road_lines_main, save_path=planning_path)
        plt.close('all')
        

        logger.info("🖼️ Images generated and saved.")

        # ---------- 8. Final Response ----------



        response = {
            "plot_coords": polygon,
            "total_plot_area": {
                "sq_m": round(total_area_m2, 2),
                "sq_ft": round(total_area_m2 * 10.7639, 2)
            },
            "roads": [{"id": f"R{i}", "coords": list(r.coords)} for i, r in enumerate(road_lines_main)],
            "front_direction": angle_to_cardinal(front_angle),
            "front_edge_index": front_idx,
            "corner_plot": frontage["corner_plot"],
            "road_count": len(road_lines_main),
            "sunlight": sunlight,
            "wind": wind,
            "boundary_dimensions": dimensions,
            
        }

        # ---------- 9. SAVE JSON ----------
        json_output_path = os.path.join(BASE_DIR, "site_response.json")
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2)
        
        print(f"\n--- SUCCESS ---\nFile saved to: {json_output_path}\n---------------", flush=True)
        return response

    except Exception as e:
        logger.error(f"💥 Internal Server Error: {str(e)}", exc_info=True)
        return {"error": str(e)}