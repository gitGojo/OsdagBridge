from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepCheck import BRepCheck_Analyzer


def build_pier_cap(
    pier_cap_top_width=3000.0,
    pier_cap_bottom_width=1200.0,
    pier_cap_depth=600.0,
    pier_cap_length=3000.0,   # MUST be passed in as actual deck width, not left default
    x_center=0.0,
    y_center=0.0,
    z_base=0.0,   # Z of TOP of pier = BOTTOM of pier cap
):
    """Trapezoidal hammerhead: narrow rectangular profile at z_base (bottom),
    wide rectangular profile at z_base + pier_cap_depth (top), lofted into a
    solid. Length runs along Y (transverse / deck-width direction)."""
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCC.Core.gp import gp_Pnt, gp_Vec
    
    # The trapezoidal profile is in the Y-Z plane.
    # We will draw it at x = x_center - (pier_cap_length / 2.0)
    # and extrude it along the +X axis by pier_cap_length.
    x_start = x_center - (pier_cap_length / 2.0)
    z0 = z_base
    z1 = z_base + pier_cap_depth
    
    bw = pier_cap_bottom_width / 2.0
    tw = pier_cap_top_width / 2.0
    
    # Points of the trapezoid in the Y-Z plane (at x_start)
    # Ordered counter-clockwise (looking from +X to -X): bottom-right, top-right, top-left, bottom-left
    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(gp_Pnt(x_start, y_center + bw, z0))
    poly.Add(gp_Pnt(x_start, y_center + tw, z1))
    poly.Add(gp_Pnt(x_start, y_center - tw, z1))
    poly.Add(gp_Pnt(x_start, y_center - bw, z0))
    poly.Close()
    
    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    
    # Extrude along the +X axis
    extrude_vec = gp_Vec(pier_cap_length, 0, 0)
    solid = BRepPrimAPI_MakePrism(face, extrude_vec).Shape()
    
    return {"pier_cap_concrete": [solid]}
