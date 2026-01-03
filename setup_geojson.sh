#!/bin/bash
# Script to download and convert GADM Czechia regions to GeoJSON

echo "============================================================"
echo "Czechia Regions GeoJSON Setup"
echo "============================================================"

# Create data directory
mkdir -p data

# Download GADM shapefile
echo ""
echo "1. Downloading GADM shapefile..."
URL="https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_CZE_shp.zip"
curl -L -o gadm41_CZE_shp.zip "$URL"

if [ ! -f gadm41_CZE_shp.zip ]; then
    echo "✗ Download failed!"
    exit 1
fi

echo "✓ Download complete"

# Extract
echo ""
echo "2. Extracting shapefile..."
unzip -q gadm41_CZE_shp.zip -d gadm_temp
echo "✓ Extraction complete"

# Find Level 1 shapefile
SHAPEFILE=$(find gadm_temp -name "*_1.shp" | head -1)

if [ -z "$SHAPEFILE" ]; then
    echo "✗ Level 1 shapefile not found!"
    exit 1
fi

echo "Found: $SHAPEFILE"

# Convert to GeoJSON
echo ""
echo "3. Converting to GeoJSON..."

# Try ogr2ogr first
if command -v ogr2ogr &> /dev/null; then
    ogr2ogr -f GeoJSON data/czechia_regions.geojson "$SHAPEFILE"
    echo "✓ Conversion complete (using ogr2ogr)"
    
    # Clean up
    rm -rf gadm41_CZE_shp.zip gadm_temp
    
    echo ""
    echo "============================================================"
    echo "SUCCESS! GeoJSON saved to: data/czechia_regions.geojson"
    echo "============================================================"
else
    echo "⚠ ogr2ogr not found"
    echo ""
    echo "Please install GDAL:"
    echo "  macOS: brew install gdal"
    echo "  Linux: apt-get install gdal-bin"
    echo ""
    echo "Or use Python with geopandas:"
    echo "  pip install geopandas"
    echo "  python download_geojson.py"
    echo ""
    echo "Shapefile extracted to: gadm_temp/"
    echo "You can convert manually using QGIS or online tools"
fi

