"""
Landfill site suitability – Regional Unit of Arcadia, Greece
=============================================================

Python (ArcPy) version of the ArcGIS ModelBuilder model used in Exercise 2.
The steps, parameters and buffer distances were exported from the original
toolbox (ArcGIS Pro 3.x, model "Model" in `ΑΣΚΗΣΗ 2.atbx`).

Requirements: ArcGIS Pro with the 3D Analyst extension.
The input layers (course data) are not included in this repository.

Workflow
--------
1. Excluded land: forested areas  ∪  karstic geological formations.
2. Terrain: contours → TIN → DEM (20 m) → slope (degrees) → 5 slope classes → polygons.
3. Distance constraints: buffers around airports, shoreline, irrigated land,
   settlements, roads, lakes, rivers and Natura 2000 sites.
4. Candidate areas = Arcadia − excluded land − (steep slopes ∪ all buffers).
5. Keep single-part polygons larger than 1 km².
"""

import os
import arcpy

# --------------------------------------------------------------------------
# Settings – adjust to your own data
# --------------------------------------------------------------------------
INPUT_GDB = r".\aivc24010.gdb"          # geodatabase with the input layers
OUTPUT_GDB = r".\aivc24010.gdb\Intermed_Results"

# Input layers (names as in the original model)
FORESTED = "Arcadia_Ilots_Forested"
FORMATIONS = "Arcadia_Formations"
CONTOURS = "Arcadia_Contours"
NUTS3 = "Arcadia_Nuts3"                 # boundary of the Regional Unit
LAKES = "Arcadia_Lakes"
AIRPORTS = "Arcadia_Airports_Polygon"
SHORELINE = "Arcadia_Soreline"
IRRIGATED = "Arcadia_Ilots_Irrigated"
SETTLEMENTS = "Arcadia_PopNet"
ROADS = "Arcadia_RoadNet"
RIVERS = "Arcadia_Rivers"
NATURA = "Arcadia_Natura"

# Buffer distances: (layer, distance, line_side)
BUFFERS = [
    (AIRPORTS,    "2840 Meters", "OUTSIDE_ONLY", "Arcadia_Airports_Poly_Buffer"),
    (SHORELINE,   "2760 Meters", "RIGHT",        "Arcadia_Soreline_Buffer"),
    (IRRIGATED,   "460 Meters",  "FULL",         "Arcadia_Ilots_Irrigated_Buffer"),
    (SETTLEMENTS, "1880 Meters", "OUTSIDE_ONLY", "Arcadia_PopNet_Buffer"),
    (ROADS,       "850 Meters",  "FULL",         "Arcadia_RoadNet_Buffer"),
    (LAKES,       "1340 Meters", "FULL",         "Arcadia_Lakes_Buffer"),
    (RIVERS,      "1340 Meters", "FULL",         "Arcadia_Rivers_Buffer"),
    (NATURA,      "1860 Meters", "FULL",         "Arcadia_Natura_Buffer"),
]

# Slope classes (degrees -> class value)
SLOPE_REMAP = arcpy.sa.RemapRange([
    [0, 5, 1],
    [5, 10, 2],
    [10, 21.815238, 3],
    [21.815238, 30.739654, 4],
    [30.739654, 84.286148, 5],
])

# Expression used in the original model to select steep-slope polygons.
# NOTE: after the reclassification above, "gridcode" holds the class values
# 1–5, so "gridcode > 10" selects no polygons. To exclude slopes above 10°
# (classes 3–5) use "gridcode >= 3" instead.
STEEP_SLOPE_WHERE = "gridcode > 10"

MIN_AREA_M2 = 1_000_000  # 1 km²

GREEK_GRID = arcpy.SpatialReference(2100)  # GGRS87 / Greek Grid


def inp(name):
    return os.path.join(INPUT_GDB, name)


def out(name):
    return os.path.join(OUTPUT_GDB, name)


def main():
    arcpy.CheckOutExtension("3D")
    arcpy.env.overwriteOutput = True

    # 1. Excluded land: forests + karstic formations ------------------------
    arcpy.analysis.Select(inp(FORMATIONS), out("Arcadia_Formations_Select"), "Karst = 1")
    arcpy.analysis.Union([inp(FORESTED), out("Arcadia_Formations_Select")],
                         out("Natura_Selected"), "ALL", gaps="GAPS")
    arcpy.analysis.Erase(inp(NUTS3), out("Natura_Selected"), out("Remain_Areas1"))

    # 2. Terrain ----------------------------------------------------------
    tin_inputs = (f"{inp(CONTOURS)} ZV2 Hard_Line <None>;"
                  f"{inp(NUTS3)} <None> Soft_Clip <None>;"
                  f"{inp(LAKES)} <None> Soft_Erase <None>")
    arcpy.ddd.CreateTin(out("Arc_TIN"), GREEK_GRID, tin_inputs, "DELAUNAY")
    arcpy.ddd.TinRaster(out("Arc_TIN"), out("Arc_Dem"), "FLOAT", "LINEAR", "CELLSIZE 20", 1)
    arcpy.ddd.Slope(out("Arc_Dem"), out("Arc_Slope"), "DEGREE", 1, "PLANAR", "METER")
    arcpy.ddd.Reclassify(out("Arc_Slope"), "VALUE", SLOPE_REMAP, out("Recl_slope"), "DATA")
    arcpy.conversion.RasterToPolygon(out("Recl_slope"), out("rslope2poly"),
                                     "SIMPLIFY", "VALUE", "SINGLE_OUTER_PART")
    arcpy.analysis.Select(out("rslope2poly"), out("Slope_poly_GT_10"), STEEP_SLOPE_WHERE)

    # 3. Distance constraints ----------------------------------------------
    exclusion_layers = [out("Slope_poly_GT_10")]
    for layer, distance, side, name in BUFFERS:
        arcpy.analysis.Buffer(inp(layer), out(name), distance, side,
                              "ROUND", "ALL", method="PLANAR")
        exclusion_layers.append(out(name))

    arcpy.analysis.Union(exclusion_layers, out("Zones_Union"), "ALL", gaps="GAPS")

    # 4. Candidate areas ----------------------------------------------------
    arcpy.analysis.Erase(out("Remain_Areas1"), out("Zones_Union"), out("Remain_Areas2"))
    arcpy.management.MultipartToSinglepart(out("Remain_Areas2"), out("Remain_Areas2_M2S"))

    # 5. Minimum area -------------------------------------------------------
    arcpy.analysis.Select(out("Remain_Areas2_M2S"), out("Final_Areas"),
                          f"Shape_Area > {MIN_AREA_M2}")

    count = int(arcpy.management.GetCount(out("Final_Areas"))[0])
    print(f"Candidate landfill sites: {count}")


if __name__ == "__main__":
    main()
