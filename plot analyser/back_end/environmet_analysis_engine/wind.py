import math

# ---------------- ANGLE HELPERS ---------------- #

def angle_diff(a, b):
    """
    Smallest angular difference between two angles (deg).
    """
    d = abs(a - b)
    return min(d, 360 - d)


def dir_to_angle(direction):
    """
    Convert cardinal direction to angle (deg).
    """
    return {
        "N": 0,
        "NE": 45,
        "E": 90,
        "SE": 135,
        "S": 180,
        "SW": 225,
        "W": 270,
        "NW": 315
    }[direction]


# ---------------- STATISTICAL WIND ---------------- #

def statistical_wind(lat):
    """
    Statistical prevailing wind model for architectural planning.
    India-focused, deterministic, no live data.
    """

    if 8 <= lat < 15:
        return {
            "primary": {"dir": "SW", "strength": "high"},
            "secondary": {"dir": "NE", "strength": "medium"},
            # "design_hints": {
            #     "ventilation_strategy": "strong cross ventilation",
            #     "preferred_air_axis": ["SW", "NE"],
            #     "room_placement": {
            #         "living": ["SW", "S"],
            #         "bedrooms": ["NE", "E"],
            #         "kitchen": ["SE"],
            #         "toilets": ["W"]
            #     },
            #     "window_strategy": {
            #         "large_operable": ["SW", "NE"],
            #         "medium": ["E"],
            #         "small": ["W"]
            #     },
            #     "courtyard": {
            #         "recommended": True,
            #         "alignment": "SW–NE"
            #     }
            # },
            
            "confidence": "high"
        }

    elif 15 <= lat < 23.5:
        return {
            "primary": {"dir": "SW", "strength": "high"},
            "secondary": {"dir": "W", "strength": "low"},
            # "design_hints": {
            #     "ventilation_strategy": "controlled cross ventilation",
            #     "preferred_air_axis": ["SW"],
            #     "room_placement": {
            #         "living": ["SW", "S"],
            #         "bedrooms": ["E", "NE"],
            #         "kitchen": ["SE"],
            #         "toilets": ["W", "NW"]
            #     },
            #     "window_strategy": {
            #         "large_operable": ["SW"],
            #         "medium": ["E"],
            #         "small": ["W"]
            #     },
            #     "courtyard": {
            #         "recommended": True,
            #         "alignment": "central"
            #     }
            # },
            
            "confidence": "medium-high"
        }

    elif 23.5 <= lat < 30:
        return {
            "primary": {"dir": "NW", "strength": "medium"},
            "secondary": {"dir": "SE", "strength": "low"},
            # "design_hints": {
            #     "ventilation_strategy": "seasonal buffered ventilation",
            #     "preferred_air_axis": ["NW", "SE"],
            #     "room_placement": {
            #         "living": ["SE", "E"],
            #         "bedrooms": ["S", "E"],
            #         "kitchen": ["SE"],
            #         "toilets": ["NW"]
            #     },
            #     "window_strategy": {
            #         "medium": ["SE", "E"],
            #         "small": ["NW", "W"]
            #     },
            #     "courtyard": {
            #         "recommended": False
            #     }
            # },
            
            "confidence": "medium"
        }

    else:
        return {
            "primary": {"dir": "W", "strength": "medium"},
            "secondary": {"dir": "E", "strength": "low"},
            # "design_hints": {
            #     "ventilation_strategy": "balanced cross ventilation",
            #     "preferred_air_axis": ["W", "E"],
            #     "room_placement": {
            #         "living": ["E"],
            #         "bedrooms": ["E", "SE"],
            #         "kitchen": ["SE"],
            #         "toilets": ["W"]
            #     },
            #     "window_strategy": 
            #         "medium": ["E"],
            #         "small": ["W"]
            #     },
            #     "courtyard": {
            #         "recommended": False
            #     }
            # },
            
            "confidence": "low"
        }


# ---------------- EDGE-LEVEL WIND EXPOSURE ---------------- #

def wind_exposure_per_edge(edges, wind):
    """
    Map wind exposure intensity to each plot edge.

    edges: [{ "angle": deg }]
    wind: output of statistical_wind()
    """

    primary_angle = dir_to_angle(wind["primary"]["dir"])
    exposure = {}

    for i, edge in enumerate(edges):
        diff = angle_diff(edge["angle"], primary_angle)

        if diff < 30:
            exposure[i] = "high"
        elif diff < 75:
            exposure[i] = "medium"
        else:
            exposure[i] = "low"

    return exposure


# ---------------- FULL WIND ANALYSIS ---------------- #

def wind_analysis(edges, latitude):
    """
    Full wind analysis including:
    - prevailing wind model
    - edge-level exposure
    - architectural design hints
    """

    wind = statistical_wind(latitude)
    exposure = wind_exposure_per_edge(edges, wind)

    return {
        "prevailing": wind,
        "edge_exposure": exposure
    }
