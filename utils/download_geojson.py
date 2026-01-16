"""
Script to download and convert GADM Czechia regions to GeoJSON
Run this script to automatically download and prepare the GeoJSON file
"""

import os
import urllib.request
import zipfile
import json
import subprocess

def download_gadm_geojson():
    """Download GADM Czechia Level 1 (regions) and convert to GeoJSON"""
    
    print("=" * 60)
    print("Downloading Czechia Regions GeoJSON from GADM")
    print("=" * 60)
    
    # GADM direct download URL for Czechia Level 1
    # Note: GADM URLs may change, this is a common pattern
    gadm_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_CZE_shp.zip"
    
    zip_path = "gadm41_CZE_shp.zip"
    extract_dir = "gadm_temp"
    geojson_path = "../data/czechia_regions.geojson"
    
    try:
        # Create data directory if it doesn't exist
        os.makedirs("../data", exist_ok=True)
        os.makedirs(extract_dir, exist_ok=True)
        
        # Download GADM shapefile
        print("\n1. Downloading GADM shapefile...")
        print(f"   URL: {gadm_url}")
        urllib.request.urlretrieve(gadm_url, zip_path)
        print("   ✓ Download complete")
        
        # Extract zip
        print("\n2. Extracting shapefile...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("   ✓ Extraction complete")
        
        # Find the Level 1 shapefile
        shapefile_path = None
        for file in os.listdir(extract_dir):
            if file.endswith("_1.shp"):
                shapefile_path = os.path.join(extract_dir, file)
                break
        
        if not shapefile_path:
            print("   ✗ Level 1 shapefile not found!")
            return False
        
        print(f"   Found: {shapefile_path}")
        
        # Convert to GeoJSON using ogr2ogr (if available) or manual conversion
        print("\n3. Converting to GeoJSON...")
        
        # Try ogr2ogr first (most reliable)
        try:
            result = subprocess.run(
                ['ogr2ogr', '-f', 'GeoJSON', geojson_path, shapefile_path],
                capture_output=True,
                text=True,
                check=True
            )
            print("   ✓ Conversion complete (using ogr2ogr)")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: use geopandas if available
            try:
                import geopandas as gpd
                gdf = gpd.read_file(shapefile_path)
                gdf.to_file(geojson_path, driver='GeoJSON')
                print("   ✓ Conversion complete (using geopandas)")
            except ImportError:
                print("   ✗ ogr2ogr not found and geopandas not installed")
                print("   Please install one of:")
                print("     - ogr2ogr: brew install gdal (macOS) or apt-get install gdal-bin (Linux)")
                print("     - geopandas: pip install geopandas")
                return False
        
        # Clean up
        print("\n4. Cleaning up...")
        os.remove(zip_path)
        import shutil
        shutil.rmtree(extract_dir)
        print("   ✓ Cleanup complete")
        
        # Verify and optimize GeoJSON
        print("\n5. Optimizing GeoJSON...")
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
        
        # Simplify geometry (reduce file size)
        simplified_features = []
        for feature in geojson.get('features', []):
            # Keep essential properties
            props = feature.get('properties', {})
            simplified_props = {
                'NAME_1': props.get('NAME_1', ''),
                'VARNAME_1': props.get('VARNAME_1', ''),
                'TYPE_1': props.get('TYPE_1', '')
            }
            feature['properties'] = simplified_props
            simplified_features.append(feature)
        
        geojson['features'] = simplified_features
        
        # Save optimized version
        with open(geojson_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))
        
        print(f"   ✓ GeoJSON saved to: {geojson_path}")
        print(f"   ✓ Features: {len(simplified_features)} regions")
        
        print("\n" + "=" * 60)
        print("SUCCESS! GeoJSON is ready for use.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nAlternative: Manual download")
        print("1. Visit: https://gadm.org/download_country.html")
        print("2. Select: Czech Republic, Level 1")
        print("3. Download shapefile")
        print("4. Convert using: ogr2ogr -f GeoJSON data/czechia_regions.geojson gadm41_CZE_1.shp")
        return False

if __name__ == '__main__':
    download_gadm_geojson()

