# OsdagBridge — Substructure Modeling & IFC Integration

> Screening task submission: parametric 3D CAD modeling of bridge substructure (piles, pile
> cap, pier, pier cap, and internal reinforcement) using `pythonOCC`, integrated into the
> existing OsdagBridge superstructure workflow and IFC export pipeline.

---

## Overview

OsdagBridge already models the bridge **superstructure** — deck, plate girders, cross bracing,
crash barriers. This contribution adds the **substructure**: the load path from the girder
bearings down to the ground, plus its internal reinforcement, fully parametric and wired into
the same visualization and IFC export pipeline the superstructure already uses.

| Before | After |
|---|---|
| Girders float with no visible support | Full pier → pier cap → pile cap → pile stack |
| Substructure `.ifc` export unsupported | Full bridge (super + sub) exports as one `.ifc` |
| No reinforcement modeling | Solid 3D rebar (not wireframe) in pier + pile cap |

---

## What's included

```
core/
├── pile/
│   └── builder.py       # 4x circular piles, 2x2 grid, parametric spacing/diameter
├── pile_cap/
│   └── builder.py       # Rectangular RC slab + 2-way rebar mesh
├── pier/
│   └── builder.py       # Circular RC column + longitudinal bars + tie rings
└── pier_cap/
    └── builder.py       # Trapezoidal hammerhead cap, spans transverse deck width
```

Wiring additions:
- `cad_generator.py` — `generate_substructure()` calls all four builders per support location,
  computes stacked elevations automatically, and merges output into the existing CAD data
  dictionary.
- `cad_3d.py` — `display_substructure()` applies concrete/rebar materials and wires the
  "Substructure" UI toggle independently of existing superstructure toggles.
- IFC wrapper — substructure shapes mapped to `IfcColumn` / `IfcBeam` / `IfcFooting` /
  `IfcReinforcingBar` with correct spatial placement relative to the existing global origin.

---

## Coordinate system

Matches the existing superstructure convention exactly, so substructure and superstructure
share one consistent frame:

```
X-axis → Longitudinal (span direction)
Y-axis → Transverse (deck width direction)
Z-axis → Vertical
Origin → Center of span, at deck/bearing level
```

Each component is placed relative to the elevation of the component beneath it (piles → pile
cap → pier → pier cap), so the full stack is always flush and gap-free regardless of parameter
changes.

---

## Parameters (all mm, all adjustable)

| Pier | | Pier Cap | | Pile Cap | | Piles | | Rebar | |
|---|---|---|---|---|---|---|---|---|---|
| diameter | 800 | top width | 3000 | length | 2200 | count | 4 (2×2) | main dia | 16 |
| height | 3000 | bottom width | 1200 | width | 1200 | diameter | 400 | main spacing | 150 |
| | | depth | 600 | depth | 600 | length | 5000 | tie dia | 8 |
| | | length | = deck width | | | spacing | 600 | tie spacing | 200 |
| | | | | | | | | cover | 40 |

`pier_cap_length` is dynamically derived from the live deck-width input — it is not a fixed
default in practice.

---

## Visuals

- **Concrete** (pier, pier cap, pile cap): light gray, semi-transparent (opacity 0.35)
- **Reinforcement**: opaque steel gray, visible through the concrete
- Both render in shaded mode (not wireframe) for a realistic BIM-style preview

---

## Running it

```bash
conda activate osdagbridge-env
cd osdagbridge/src
python -m osdagbridge.desktop
```

In the app: enter span/carriageway inputs → **Design** → check **Substructure** (independent
of the **Bridge** toggle, both can be active together) → rotate to isometric view.

To export the full model (super + substructure) to IFC:
**File → Save 3D CAD Model → Save as type: .ifc**

---

## Testing

Each builder is independently testable outside the full app:

```bash
python -c "
from core.pier.builder import build_pier
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add

result = build_pier()
box = Bnd_Box()
brepbndlib_Add(result['pier_concrete'][0], box)
print(box.Get())
"
```

This bounding-box-first testing approach was essential during development — see the
**Challenges** section of the accompanying report for why isolated component testing catches
defect classes that full end-to-end testing alone can miss.

---

## Known limitations / future work

- Reinforcement is fully modeled for **pier** and **pile cap**; pier cap and pile reinforcement
  are deferred (lower priority — not clearly visible in the reference outcome images).
- Pile arrangement is fixed at a 2×2 grid; configurable count/pattern is a natural next step.
- IFC export has been validated against one BIM viewer; broader tool coverage is future work.

---



## Acknowledgments

Built on top of the existing OsdagBridge (FOSSEE / IIT Bombay) architecture. Superstructure
modules (girder, deck, cross bracing) were used as the reference pattern for how substructure
builders should structure their return values and integrate with the display pipeline.
