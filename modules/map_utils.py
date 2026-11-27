from pathlib import Path

import geopandas as gpd
import streamlit as st


@st.cache_data
def load_area_geodata(area_type):
    """
    Load and prepare geographical polygons for the three
    Magasinstatistikk area types.

    Returns geometries in WGS84 (EPSG:4326), ready for Plotly.
    """

    project_root = Path(__file__).resolve().parents[1]

    # ---------------------------------------------------------
    # Electricity price areas: NO1–NO5
    # ---------------------------------------------------------
    if area_type == "EL":

        shapefile_dir = (
            project_root
            / "data"
            / "shapefiles"
            / "elspot"
        )

        shapefile = next(
            shapefile_dir.glob("*.shp")
        )

        gdf = gpd.read_file(shapefile)

        gdf["area_number"] = (
            gdf["budomr"]
            .astype(str)
            .str.extract(r"(\d+)")
            .astype(int)
        )

        gdf["area_name"] = (
            "NO"
            + gdf["area_number"].astype(str)
        )

        gdf = gdf[
            [
                "area_number",
                "area_name",
                "geometry",
            ]
        ]

    # ---------------------------------------------------------
    # Water / reservoir regions: VASS1–VASS3
    # ---------------------------------------------------------
    elif area_type == "VASS":

        shapefile_dir = (
            project_root
            / "data"
            / "shapefiles"
            / "nve_regions"
        )

        shapefile = next(
            shapefile_dir.glob("*.shp")
        )

        regions = gpd.read_file(
            shapefile,
            encoding="utf-8",
        )

        vass_mapping = {
            1: ["RS", "RØ"],
            2: ["RV"],
            3: ["RM", "RN"],
        }

        rows = []

        for area_number, region_codes in vass_mapping.items():

            selected = regions[
                regions["REGION"].isin(
                    region_codes
                )
            ]

            rows.append(
                {
                    "area_number": area_number,
                    "area_name": f"VASS{area_number}",
                    "geometry": (
                        selected.geometry.union_all()
                    ),
                }
            )

        gdf = gpd.GeoDataFrame(
            rows,
            crs=regions.crs,
        )

    # ---------------------------------------------------------
    # Norway as a whole
    # ---------------------------------------------------------
    elif area_type == "NO":

        shapefile_dir = (
            project_root
            / "data"
            / "shapefiles"
            / "nve_regions"
        )

        shapefile = next(
            shapefile_dir.glob("*.shp")
        )

        regions = gpd.read_file(
            shapefile,
            encoding="utf-8",
        )

        gdf = gpd.GeoDataFrame(
            [
                {
                    "area_number": 0,
                    "area_name": "Norway",
                    "geometry": (
                        regions.geometry.union_all()
                    ),
                }
            ],
            crs=regions.crs,
        )

    else:
        raise ValueError(
            f"Unsupported area type: {area_type}"
        )

    return gdf.to_crs(
        epsg=4326
    )