from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder


def build_pile_cap(
    pile_cap_length=2200.0,
    pile_cap_width=1200.0,
    pile_cap_depth=600.0,
    rebar_main_diameter=16.0,
    rebar_spacing_longitudinal=150.0,
    rebar_cover=40.0,
    x_center=0.0,
    y_center=0.0,
    z_top=0.0,   # Z of TOP of piles = BOTTOM face of this pile cap
):
    """Box's BOTTOM face sits at z_top, extends upward (+Z) by pile_cap_depth.
    This must equal the z_top used in build_piles() for the same support, so
    the cap sits flush on top of the piles with zero gap/overlap."""

    corner = gp_Pnt(
        x_center - pile_cap_length / 2.0,
        y_center - pile_cap_width / 2.0,
        z_top,  # <-- bottom face AT z_top, box grows upward from here
    )
    box = BRepPrimAPI_MakeBox(corner, pile_cap_length, pile_cap_width, pile_cap_depth).Shape()

    # 2-way orthogonal rebar mesh near the bottom face of the slab
    mesh_bars = []
    x_min = x_center - pile_cap_length / 2.0 + rebar_cover
    x_max = x_center + pile_cap_length / 2.0 - rebar_cover
    y_min = y_center - pile_cap_width / 2.0 + rebar_cover
    y_max = y_center + pile_cap_width / 2.0 - rebar_cover
    bar_radius = rebar_main_diameter / 2.0
    z_mesh = z_top + rebar_cover + bar_radius  # relative to corrected bottom face

    n_bars_x = max(2, int((x_max - x_min) / rebar_spacing_longitudinal)) + 1
    actual_spacing_x = (x_max - x_min) / (n_bars_x - 1)
    n_bars_y = max(2, int((y_max - y_min) / rebar_spacing_longitudinal)) + 1
    actual_spacing_y = (y_max - y_min) / (n_bars_y - 1)

    # bars running along X
    for i in range(n_bars_y):
        y = y_min + i * actual_spacing_y
        ax2 = gp_Ax2(gp_Pnt(x_min, y, z_mesh), gp_Dir(1, 0, 0), gp_Dir(0, 1, 0))
        bar = BRepPrimAPI_MakeCylinder(ax2, bar_radius, x_max - x_min).Shape()
        mesh_bars.append(bar)

    # bars running along Y, stacked one bar-diameter above the X-layer
    z_trans = z_mesh + rebar_main_diameter
    for i in range(n_bars_x):
        x = x_min + i * actual_spacing_x
        ax2 = gp_Ax2(gp_Pnt(x, y_min, z_trans), gp_Dir(0, 1, 0), gp_Dir(0, 0, 1))
        bar = BRepPrimAPI_MakeCylinder(ax2, bar_radius, y_max - y_min).Shape()
        mesh_bars.append(bar)

    return {"pile_cap_concrete": [box], "pile_cap_rebar": mesh_bars}
