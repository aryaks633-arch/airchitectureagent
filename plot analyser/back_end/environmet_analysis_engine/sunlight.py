import math

# ---------------- CONSTANTS ---------------- #

# Maximum solar declination (summer solstice)
SUMMER_DECLINATION = 23.44


# ---------------- SOLAR GEOMETRY ---------------- #

def sun_alt_azimuth(lat, dec, h):
    """
    Calculate sun altitude and azimuth.
    lat: latitude (deg)
    dec: declination (deg)
    h: hour angle (deg)
    """

    lat, dec, h = map(math.radians, (lat, dec, h))

    alt = math.asin(
        math.sin(lat) * math.sin(dec) +
        math.cos(lat) * math.cos(dec) * math.cos(h)
    )

    az = math.atan2(
        math.sin(h),
        math.cos(h) * math.sin(lat) - math.tan(dec) * math.cos(lat)
    )

    return math.degrees(alt), (math.degrees(az) + 180) % 360


# ---------------- ANGLE HELPERS ---------------- #

def edge_normal(angle):
    """
    Outward-facing normal of a plot edge.
    """
    return (angle + 90) % 360


def angle_diff(a, b):
    """
    Smallest angular difference between two angles.
    """
    d = abs(a - b)
    return min(d, 360 - d)


# ---------------- SUN EXPOSURE (PHYSICS) ---------------- #

def edge_sun_exposure(edge_angle, latitude):
    """
    Classify sunlight exposure for one plot edge
    using summer sun path sampling.
    """

    normal = edge_normal(edge_angle)
    score = 0

    # Sample sun position from 8 AM to 4 PM
    for hour in range(-4, 5):
        alt, az = sun_alt_azimuth(latitude, SUMMER_DECLINATION, hour * 15)

        if alt <= 0:
            continue

        diff = angle_diff(normal, az)

        if diff < 45:
            score += 2
        elif diff < 90:
            score += 1

    if score >= 10:
        return "harsh"
    if score >= 6:
        return "strong"
    if score >= 3:
        return "moderate"
    return "soft"


# ---------------- DESIGN INTERPRETATION ---------------- #

# def sunlight_design_hint(exposure):
#     """
#     Convert sunlight exposure into architectural design hints.
#     """

#     if exposure == "soft":
#         return {
#             "suitability": "excellent",
#             "recommended_rooms": ["bedroom", "study", "living"],
#             "window_strategy": "large clear windows",
#             "shading": "not required",
#             "notes": "Comfortable daylight with minimal heat gain"
#         }

#     if exposure == "moderate":
#         return {
#             "suitability": "very_good",
#             "recommended_rooms": ["living", "dining", "bedroom"],
#             "window_strategy": "medium to large windows",
#             "shading": "light shading recommended",
#             "notes": "Balanced daylight and thermal comfort"
#         }

#     if exposure == "strong":
#         return {
#             "suitability": "conditional",
#             "recommended_rooms": ["kitchen", "living", "home_office"],
#             "window_strategy": "controlled-size windows",
#             "shading": "mandatory (chajjas / louvers)",
#             "notes": "Good daylight but requires heat control"
#         }

#     if exposure == "harsh":
#         return {
#             "suitability": "poor",
#             "recommended_rooms": ["toilet", "staircase", "store", "utility"],
#             "window_strategy": "small or high-level openings",
#             "shading": "heavy shading or blank wall",
#             "notes": "Avoid habitable spaces on this edge"
#         }


# ---------------- PUBLIC API ---------------- #

def sunlight_analysis(edges, latitude):
    """
    Full sunlight analysis per plot edge.
    Returns exposure + architectural design hints.
    """

    result = {}

    for i, edge in enumerate(edges):
        exposure = edge_sun_exposure(edge["angle"], latitude)

        result[i] = {
            "exposure": exposure,
            # "design_hint": sunlight_design_hint(exposure)
        }

    return result
