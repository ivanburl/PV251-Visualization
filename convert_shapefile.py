"""
Simple script to convert existing shapefile to GeoJSON
Uses the already downloaded GADM shapefile
"""

import os
import json

# Try geopandas first
try:
    import geopandas as gpd
    
    shapefile = "gadm_temp/gadm41_CZE_1.shp"
    if os.path.exists(shapefile):
        print("Converting shapefile to GeoJSON...")
        gdf = gpd.read_file(shapefile)
        
        # Simplify properties
        gdf = gdf[['NAME_1', 'VARNAME_1', 'TYPE_1', 'geometry']]
        
        # Save as GeoJSON
        os.makedirs('data', exist_ok=True)
        gdf.to_file('data/czechia_regions.geojson', driver='GeoJSON')
        
        print(f"✓ GeoJSON saved to: data/czechia_regions.geojson")
        print(f"✓ Regions: {len(gdf)}")
        print("\nRegions:")
        for name in gdf['NAME_1']:
            print(f"  - {name}")
    else:
        print(f"✗ Shapefile not found: {shapefile}")
        print("Please run download_geojson.py first")
        
except ImportError:
    print("geopandas not installed")
    print("\nPlease install:")
    print("  pip install geopandas")
    print("\nOr use ogr2ogr:")
    print("  ogr2ogr -f GeoJSON data/czechia_regions.geojson gadm_temp/gadm41_CZE_1.shp")

