import requests
import time
from shapely.geometry import LineString

# ---------------- CONFIG ---------------- #

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter"
]

ROAD_TOUCH_THRESHOLD = 0.00005   # ~5–6 m
BBOX_PADDING = 0.0001            # ~10–12 m

# Only real roads (NO footpaths / park paths)
HIGHWAY_FILTER = "^(primary|secondary|tertiary|residential|trunk|unclassified)$"


# ---------------- BBOX ---------------- #

def bounding_box(plot_coords, padding=BBOX_PADDING):
    lons = [p[0] for p in plot_coords]
    lats = [p[1] for p in plot_coords]

    return {
        "south": min(lats) - padding,
        "west":  min(lons) - padding,
        "north": max(lats) + padding,
        "east":  max(lons) + padding
    }


# ---------------- FETCH ROADS ---------------- #

def fetch_roads_for_plot(plot_coords, retries=2):
    bbox = bounding_box(plot_coords)

    query = f"""
    [out:json][timeout:10];
    way["highway"~"{HIGHWAY_FILTER}"](
        {bbox['south']},
        {bbox['west']},
        {bbox['north']},
        {bbox['east']}
    );
    out geom;
    """

    for attempt in range(retries):
        try:
            url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]
            r = requests.post(url, data=query, timeout=15)
            r.raise_for_status()
            return r.json().get("elements", [])
        except requests.exceptions.RequestException as e:
            print(f"⚠ Overpass failed ({attempt+1}): {e}")
            time.sleep(1)

    return []


# ---------------- GEOMETRY ---------------- #

def road_geometries(osm_roads):
    roads = []
    for r in osm_roads:
        if "geometry" not in r:
            continue
        coords = [(p["lon"], p["lat"]) for p in r["geometry"]]
        if len(coords) >= 2:
            roads.append(LineString(coords))
    return roads


def plot_edges_to_lines(plot_coords):
    return [
        LineString([plot_coords[i], plot_coords[i + 1]])
        for i in range(len(plot_coords) - 1)
    ]


# ---------------- FRONTAGE ---------------- #

def detect_frontage(plot_edges, road_lines):
    """
    Detects the front edge of the plot based on nearest meaningful road adjacency.
    """

    # No roads → longest edge fallback
    if not road_lines:
        longest = max(
            range(len(plot_edges)),
            key=lambda i: plot_edges[i].length
        )
        return {
            "front_edge_index": longest,
            "corner_plot": False,
            "touching_edges": []
        }

    edge_scores = []

    for idx, edge in enumerate(plot_edges):
        for road in road_lines:
            dist = edge.distance(road)

            # Projection length = how much the edge aligns with road
            try:
                proj = edge.intersection(road.buffer(ROAD_TOUCH_THRESHOLD * 2))
                proj_len = proj.length if not proj.is_empty else 0
            except Exception:
                proj_len = 0

            edge_scores.append({
                "idx": idx,
                "distance": dist,
                "projection": proj_len
            })

    # Prefer edges with:
    # 1. Road touch / projection
    # 2. Smaller distance
    edge_scores.sort(
        key=lambda e: (
            e["distance"] > ROAD_TOUCH_THRESHOLD,   # touching edges first
            -e["projection"],                       # longer overlap preferred
            e["distance"]                           # then closest
        )
    )

    front_edge_index = edge_scores[0]["idx"]

    touching_edges = list({
        e["idx"] for e in edge_scores
        if e["distance"] <= ROAD_TOUCH_THRESHOLD
    })

    return {
        "front_edge_index": front_edge_index,
        "corner_plot": len(touching_edges) >= 2,
        "touching_edges": touching_edges
    }

def fetch_all_roads_for_plot(plot_coords, retries=2):
    """
    Fetch ALL highway types (including footpaths, service roads, paths)
    Used ONLY for context visualization.
    """
    bbox = bounding_box(plot_coords)

    query = f"""
    [out:json][timeout:10];
    way["highway"](
        {bbox['south']},
        {bbox['west']},
        {bbox['north']},
        {bbox['east']}
    );
    out geom;
    """

    for attempt in range(retries):
        try:
            url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]
            response = requests.post(url, data=query, timeout=15)
            response.raise_for_status()
            return response.json().get("elements", [])
        except requests.exceptions.RequestException as e:
            print(f"⚠ Overpass(all roads) failed: {e}")
            time.sleep(1)

    return []
