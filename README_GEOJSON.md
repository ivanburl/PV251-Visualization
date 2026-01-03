# Czechia Regions GeoJSON Setup

## Quick Start

### Option 1: Automatic Download (Recommended)

Run the download script:

```bash
python download_geojson.py
```

This will:
1. Download GADM Czechia Level 1 shapefile
2. Convert to GeoJSON
3. Optimize and save to `data/czechia_regions.geojson`

**Requirements:**
- `ogr2ogr` (GDAL) - OR -
- `geopandas` Python package

Install GDAL:
- macOS: `brew install gdal`
- Linux: `apt-get install gdal-bin`
- Windows: Download from OSGeo4W

Or install geopandas:
```bash
pip install geopandas
```

### Option 2: Manual Download

1. Visit: https://gadm.org/download_country.html
2. Select: **Czech Republic**, **Level 1** (regions/kraje)
3. Download shapefile (zip)
4. Extract and convert:

```bash
ogr2ogr -f GeoJSON data/czechia_regions.geojson gadm41_CZE_1.shp
```

## GeoJSON Structure

The GeoJSON uses GADM structure:
- `properties.NAME_1`: Czech region names (e.g., "Praha", "Středočeský kraj")
- `properties.VARNAME_1`: English names (e.g., "Prague", "Central Bohemia")
- `properties.TYPE_1`: Region type

## Region Name Mapping

The application automatically maps between:
- **Dataset names** (English): "Prague", "Central Bohemia", etc.
- **GADM names** (Czech): "Praha", "Středočeský kraj", etc.

Mapping is handled by `normalize_region_name()` in `utils.py`.

## Verification

After downloading, verify the GeoJSON:

```python
import json

with open('data/czechia_regions.geojson', 'r') as f:
    geojson = json.load(f)

print(f"Regions: {len(geojson['features'])}")
for feature in geojson['features']:
    print(f"  - {feature['properties'].get('NAME_1', 'Unknown')}")
```

Expected: 14 regions

## Troubleshooting

**Problem:** GeoJSON not found
- Check file path: `data/czechia_regions.geojson`
- Verify file exists: `ls data/czechia_regions.geojson`

**Problem:** Regions not matching
- Check region names in your dataset
- Verify GADM NAME_1 values match normalization function
- Check console output for mapping messages

**Problem:** Choropleth not showing
- Verify GeoJSON is valid: `python -c "import json; json.load(open('data/czechia_regions.geojson'))"`
- Check console for "Choropleth map created" message
- If fallback to markers, check region name matching

## File Location

The GeoJSON should be placed at:
```
data/czechia_regions.geojson
```

The application will automatically detect and use it when available.

