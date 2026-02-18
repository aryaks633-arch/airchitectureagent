import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from site_inteligence_engine.boundary_dimensions import edge_length_m
def draw_plus_compass(ax, plot_coords, corner="top-right", size=0.03):
    """
    Draws a minimal '+' compass marker with 'N'
    size: relative to plot size (smaller = subtler)
    """

    px = [p[0] for p in plot_coords]
    py = [p[1] for p in plot_coords]

    minx, maxx = min(px), max(px)
    miny, maxy = min(py), max(py)

    dx = maxx - minx
    dy = maxy - miny

    margin_x = dx * 0.08
    margin_y = dy * 0.08

    if corner == "top-right":
        cx = maxx + margin_x
        cy = maxy - margin_y
    elif corner == "top-left":
        cx = minx - margin_x
        cy = maxy - margin_y
    elif corner == "bottom-left":
        cx = minx - margin_x
        cy = miny + margin_y
    else:  # bottom-right
        cx = maxx + margin_x
        cy = miny + margin_y

    half = size * min(dx, dy)

    # vertical line
    ax.plot(
        [cx, cx],
        [cy - half, cy + half],
        color="black",
        linewidth=1
    )

    # horizontal line
    ax.plot(
        [cx - half, cx + half],
        [cy, cy],
        color="black",
        linewidth=1
    )

    # N label
    ax.text(
        cx,
        cy + half * 1.4,
        "N",
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold"
    )

def draw_boundary_dimensions(ax, plot_coords, unit="m"):
    px = [p[0] for p in plot_coords]
    py = [p[1] for p in plot_coords]

    for i in range(len(plot_coords) - 1):
        p1 = plot_coords[i]
        p2 = plot_coords[i + 1]

        length_m = edge_length_m(p1, p2)

        if unit == "ft":
            text = f"{length_m * 3.28084:.1f} ft"
        else:
            text = f"{length_m:.1f} m"

        xm = (p1[0] + p2[0]) / 2
        ym = (p1[1] + p2[1]) / 2

        # small outward offset
        dx = p2[1] - p1[1]
        dy = -(p2[0] - p1[0])
        norm = (dx**2 + dy**2) ** 0.5 or 1

        offset = 0.00002
        ox = xm + offset * dx / norm
        oy = ym + offset * dy / norm

        ax.text(
            ox, oy,
            text,
            fontsize=8,
            ha="center",
            va="center",
            color="black",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                alpha=0.8,
                pad=0.2
            )
        )

def draw_planning_map(
    plot_coords,
    road_lines_main,
    save_path="site_planning.png"
):
    """
    Planning view:
    - only main roads
    - clean plot boundary
    - edge indices
    """

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("white")

    plot_poly = Polygon(plot_coords)
    plan_area = plot_poly.buffer(0.00015)

    # draw main roads
    for road in road_lines_main:
        clipped = road.intersection(plan_area)
        if clipped.is_empty:
            continue

        geoms = clipped.geoms if clipped.geom_type == "MultiLineString" else [clipped]
        for g in geoms:
            x, y = g.xy
            ax.plot(
                x, y,
                color="black",
                linewidth=3,
                solid_capstyle="round"
            )

    # plot boundary
    px = [p[0] for p in plot_coords]
    py = [p[1] for p in plot_coords]
    ax.plot(px, py, color="#333333", linewidth=1.8)

    # edge indices
    for i in range(len(plot_coords) - 1):
        xm = (plot_coords[i][0] + plot_coords[i + 1][0]) / 2
        ym = (plot_coords[i][1] + plot_coords[i + 1][1]) / 2
        ax.text(
            xm, ym, str(i),
            ha="center",
            va="center",
            fontsize=9,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none")
        )
    draw_plus_compass(ax, plot_coords, corner="top-right", size=0.02)
    draw_boundary_dimensions(ax, plot_coords, unit="ft")

    ax.set_title("Planning View (Main Roads Only)", fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()

    print(f"✅ Planning map saved as {save_path}")
