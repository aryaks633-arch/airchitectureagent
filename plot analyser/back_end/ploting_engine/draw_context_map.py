import matplotlib.pyplot as plt
from shapely.geometry import Polygon

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

def draw_context_map(
    plot_coords,
    road_lines_all,
    save_path="site_context.png"
):
    """
    Context view:
    - all roads + paths
    - wide buffer
    """

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("white")

    plot_poly = Polygon(plot_coords)
    context_area = plot_poly.buffer(0.0003)

    # draw all roads & paths
    for road in road_lines_all:
        clipped = road.intersection(context_area)
        if clipped.is_empty:
            continue

        geoms = clipped.geoms if clipped.geom_type == "MultiLineString" else [clipped]
        for g in geoms:
            x, y = g.xy
            ax.plot(x, y, color="#777777", linewidth=1)

    # plot boundary
    px = [p[0] for p in plot_coords]
    py = [p[1] for p in plot_coords]
    ax.plot(px, py, color="black", linewidth=1.2)

    draw_plus_compass(ax, plot_coords, corner="top-right", size=0.025)


    ax.set_title("Context View (All Roads & Paths)", fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()

    print(f"✅ Context map saved as {save_path}")
