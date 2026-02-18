from pyproj import Geod

geod = Geod(ellps="WGS84")

def edge_length_m(p1, p2):
    """
    Calculate geodesic distance between two (lon, lat) points in meters
    """
    _, _, dist = geod.inv(
        p1[0], p1[1],
        p2[0], p2[1]
    )
    return dist
def edge_length_meters(p1, p2):
    """
    p1, p2 = (lon, lat)
    returns distance in meters
    """
    _, _, dist = geod.inv(p1[0], p1[1], p2[0], p2[1])
    return dist


def plot_edge_dimensions(polygon_coords):
    """
    polygon_coords: list of (lon, lat)
    returns list of edge lengths in meters
    """

    dimensions = []

    for i in range(len(polygon_coords) - 1):
        p1 = polygon_coords[i]
        p2 = polygon_coords[i + 1]

        length_m = edge_length_meters(p1, p2)

        dimensions.append({
            "edge_index": i,
            "length_m": round(length_m, 2),
            "length_ft": round(length_m * 3.28084, 2)
        })

    return dimensions
