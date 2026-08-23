import math
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeTorus


def build_pier(
    pier_diameter=800.0,
    pier_height=3000.0,
    rebar_main_diameter=16.0,
    rebar_spacing_longitudinal=150.0,
    rebar_transverse_diameter=8.0,
    rebar_spacing_transverse=200.0,
    rebar_cover=40.0,
    x_center=0.0,
    y_center=0.0,
    z_base=0.0,   # Z of TOP of pile cap = BOTTOM of pier
):
    """Concrete cylinder's BOTTOM face sits at z_base, extends upward (+Z) by
    pier_height. z_base MUST equal (pile_cap z_top + pile_cap_depth) for the
    same support, so the pier sits flush on top of the pile cap."""

    axis = gp_Ax2(gp_Pnt(x_center, y_center, z_base), gp_Dir(0, 0, 1))
    concrete = BRepPrimAPI_MakeCylinder(axis, pier_diameter / 2.0, pier_height).Shape()

    rebar_radius = (pier_diameter / 2.0) - rebar_cover
    n_main_bars = max(6, int((2 * math.pi * rebar_radius) / rebar_spacing_longitudinal))
    main_bars = []
    for i in range(n_main_bars):
        angle = 2 * math.pi * i / n_main_bars
        bx = x_center + rebar_radius * math.cos(angle)
        by = y_center + rebar_radius * math.sin(angle)
        base = gp_Pnt(bx, by, z_base)
        bar_axis = gp_Ax2(base, gp_Dir(0, 0, 1))
        bar = BRepPrimAPI_MakeCylinder(bar_axis, rebar_main_diameter / 2.0, pier_height).Shape()
        main_bars.append(bar)

    tie_shapes = []
    n_ties = max(1, int(pier_height / rebar_spacing_transverse))
    for i in range(n_ties):
        z = z_base + i * rebar_spacing_transverse
        tie_center = gp_Pnt(x_center, y_center, z)
        tie_axis = gp_Ax2(tie_center, gp_Dir(0, 0, 1))
        tie = BRepPrimAPI_MakeTorus(
            tie_axis, rebar_radius, rebar_transverse_diameter / 2.0
        ).Shape()
        tie_shapes.append(tie)

    return {
        "pier_concrete": [concrete],
        "rebar_long": main_bars,
        "rebar_trans": tie_shapes,
    }
