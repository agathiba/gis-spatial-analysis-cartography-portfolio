# Applied GIS, Spatial Analysis & Automated Suitability Modeling Portfolio

A comprehensive portfolio of spatial modeling, geodemographic cartography, and spatial statistics developed during postgraduate studies in GIS and Visual Computing.

---

## 📌 Projects & Modules Overview

### 1. Spatial Statistics & Urban Amenity Analysis (KDE)
* **Objective:** Spatial analysis of residential property valuations across Palaio Faliro (Athens, Greece).
* **Methodology:** Applied **Kernel Density Estimation (KDE)** to identify spatial clustering and price hot-spots.
* **Spatial Drivers:** Evaluated distance-decay impacts of coastal proximity, hydrographic barriers, and public infrastructure accessibility.
* 📄 **[Technical Note (PDF - Greek)](./Exercise_1_1_Spatial_Density_KDE.pdf)**

<p align="center">
  <img src="images/kde_property_values.png" width="600" alt="Kernel density of residential property values, Palaio Faliro (Athens)">
  <br><em>Kernel density of residential property values, Palaio Faliro (Athens)</em>
</p>

* **Attribute & Spatial Queries (ArcGIS Pro):** Combined attribute filters with distance and proximity analysis to answer three housing questions – (1) 3-bedroom homes with parking and fireplace, farthest from the coastline, with the lowest price per m²; (2) 2-bedroom homes with parking, built in the last decade, closest to a metro station, with the highest price; (3) homes above 20 m elevation located 200–300 m from the main rivers.

<p align="center">
  <img src="images/faliro_property_queries.png" alt="Three map layouts showing the results of the housing queries in Palaio Faliro">
  <br><em>Results of the three housing queries in Palaio Faliro (map layouts in ArcGIS Pro)</em>
</p>

---

### 2. Geodemographic Analysis & Thematic Cartography (QGIS)
* **Objective:** National-scale mapping of economic activity and workforce shifts across Greek prefectures using census records (1991–2001).
* **Spatial Data Pipeline:** 
  * Tabular data cleaning, attribute structuring, and ratio index calculations.
  * Spatial joins and topological vector preprocessing using the **Dissolve** tool to resolve duplicate administrative boundaries.
  * Statistical classification via **Natural Breaks (Jenks)** based on distribution histograms.
  * Professional print layout production at 1:4,000,000 scale featuring thematic legends, scale bars, north arrows, and spatial insets.
* 📄 **[Technical Report (PDF - Greek)](./Exercise_1_2_Socioeconomic_Thematic_Cartography.pdf)**

<p align="center">
  <img src="images/thematic_maps_greece.png" alt="Thematic maps of economic activity across Greek prefectures (QGIS)">
  <br><em>Thematic maps of economic activity across Greek prefectures (QGIS)</em>
</p>

---

### 3. Multi-Criteria Site Suitability Modeling (ArcGIS ModelBuilder)
* **Objective:** Automated spatial site selection for a Sanitary Landfill (Χ.Υ.Τ.Υ.) across the Regional Unit of Arcadia, Greece.
* **Surface & Terrain Processing:** 
  * Interpolated Triangulated Irregular Networks (**TIN**) into high-resolution Digital Elevation Models (**DEM**).
  * Extracted slope gradients (**Slope**) and reclassified terrain suitability thresholds.
* **Spatial Multi-Criteria Decision Analysis (MCDA):**
  * Automated geoprocessing pipeline constructed in **ArcGIS ModelBuilder**.
  * Applied buffer exclusion zones around airports, shoreline, irrigated land, settlements, roads, lakes, rivers and Natura 2000 sites.
  * Integrated vector overlay operations (Union, Erase, Multipart to Singlepart, Select) to isolate compliant land parcels larger than 1 km².
  * 🐍 **[Python (ArcPy) version of the model](./modelbuilder/landfill_site_suitability.py)**, exported from the original ModelBuilder toolbox.
* 📄 **[Final Cartographic Deliverable (PDF)](./Exercise_2_Landfill_Suitability_Arcadia_Map.pdf)**
* 📄 **[Automated ModelBuilder Architecture (PDF)](./Exercise_2_MCDA_ModelBuilder_Workflow.pdf)**

<p align="center">
  <img src="images/landfill_suitability_arcadia.png" alt="Final map: suitable landfill sites in the Regional Unit of Arcadia">
  <br><em>Final map: suitable landfill sites in the Regional Unit of Arcadia</em>
</p>

<p align="center">
  <img src="images/modelbuilder_workflow.png" alt="Automated suitability model in ArcGIS ModelBuilder">
  <br><em>Automated suitability model in ArcGIS ModelBuilder</em>
</p>

#### Model workflow

```mermaid
flowchart LR
    A[Forested areas] --> U1((Union))
    B[Geological formations] -->|Select Karst = 1| U1
    U1 --> E1[/Erase from Arcadia/]
    N[Arcadia boundary] --> E1
    C[Contours, lakes, boundary] --> T[Create TIN] --> D[TIN to DEM 20 m] --> S[Slope °] --> R[Reclassify 5 classes] --> P[Raster to Polygon]
    P -->|steep slopes| U2((Union))
    X[8 buffer zones] --> U2
    E1 --> E2[/Erase exclusion zones/]
    U2 --> E2
    E2 --> M[Multipart to Singlepart] --> F[Select area > 1 km²] --> OUT[(Candidate sites)]
```

| Exclusion layer | Buffer distance | Side |
| :--- | ---: | :--- |
| Airports | 2,840 m | outside only |
| Shoreline | 2,760 m | right |
| Settlements | 1,880 m | outside only |
| Natura 2000 sites | 1,860 m | full |
| Lakes | 1,340 m | full |
| Rivers | 1,340 m | full |
| Roads | 850 m | full |
| Irrigated land | 460 m | full |

> **Note:** in the original model the steep-slope polygons are selected with `gridcode > 10`, but after reclassification the values are 1–5, so this criterion selects no polygons. Excluding slopes above 10° requires `gridcode >= 3`; the Python script keeps the original expression and documents the correction.

---

## 🛠️ Software & Technical Stack
* **GIS Suites:** ArcGIS Pro / ArcMap (ModelBuilder, 3D Analyst, Spatial Analyst), QGIS
* **Techniques:** Multi-Criteria Decision Analysis (MCDA), Kernel Density Estimation (KDE), Terrain Analysis, Automated Geoprocessing (ModelBuilder, ArcPy), Vector Overlays, Attribute & Spatial Queries
