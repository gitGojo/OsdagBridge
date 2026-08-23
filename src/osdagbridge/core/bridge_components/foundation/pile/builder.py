from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder


def build_piles(
    n_piles_per_cap=4,
    pile_diameter=400.0,
    pile_length=5000.0,
    pile_spacing=600.0,
    x_center=0.0,
    y_center=0.0,
    z_top=0.0,   # Z of the TOP of the piles (= bottom of pile cap)
):
    """Returns 4 cylinders in a 2x2 grid. Each pile's TOP face is at z_top,
    extending downward (-Z) by pile_length."""
    shapes = []
    pile_rebar = []
    half = pile_spacing / 2.0
    offsets = [(-half, -half), (-half, half), (half, -half), (half, half)]
    
    rebar_cover = 50.0
    rebar_dia = 16.0
    
    for dx, dy in offsets:
        base = gp_Pnt(x_center + dx, y_center + dy, z_top - pile_length)
        axis = gp_Ax2(base, gp_Dir(0, 0, 1))  # extrudes +Z from base up to z_top
        cyl = BRepPrimAPI_MakeCylinder(axis, pile_diameter / 2.0, pile_length).Shape()
        shapes.append(cyl)
        
        # Add simple longitudinal rebar inside each pile (4 bars per pile)
        r_offset = pile_diameter / 2.0 - rebar_cover
        for rx, ry in [(-r_offset, 0), (r_offset, 0), (0, -r_offset), (0, r_offset)]:
            r_base = gp_Pnt(x_center + dx + rx, y_center + dy + ry, z_top - pile_length + 50)
            r_axis = gp_Ax2(r_base, gp_Dir(0, 0, 1))
            r_cyl = BRepPrimAPI_MakeCylinder(r_axis, rebar_dia / 2.0, pile_length - 100).Shape()
            pile_rebar.append(r_cyl)

    assert len(shapes) == 4, f"expected 4 piles, got {len(shapes)}"
    return {"piles": shapes, "pile_rebar": pile_rebar}
