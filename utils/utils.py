"""
Utility functions for creating visualizations
"""

import json
import os

# Color schemes matching PDF design
# Change colors here to modify severity color coding


# Sequential color palette for density visualization (yellow to red)
# Used for map density and severity encoding
DENSITY_COLORS = ['#fff9c4', '#fff59d', '#ffeb3b', '#ffc107', '#ff9800', '#f57c00', '#e65100', '#bf360c']

_GLOBAL_GEOJSON_CACHE = None

def _init_geojson():
    """Load Czechia regions GeoJSON if available"""
    # Check these paths in order (add more paths if needed)
    global _GLOBAL_GEOJSON_CACHE
    geojson_paths = [
        'data/czechia_regions.geojson',
        'czechia_regions.geojson',
        'data/cze_adm1.geojson'
    ]

    for path in geojson_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    _GLOBAL_GEOJSON_CACHE = json.load(f)
                    break
            except Exception as e:
                print(f"Error loading GeoJSON from {path}: {e}")


_init_geojson()


def load_geojson():
    if _GLOBAL_GEOJSON_CACHE is None:
        return None
    return json.loads(json.dumps(_GLOBAL_GEOJSON_CACHE))

def normalize_region_name(region_name):
    """
    Normalize region names to match between data and GADM GeoJSON
    GADM uses Czech names in NAME_1 field (may be shortened)
    """
    if not region_name:
        return region_name
    
    # GADM NAME_1 variations -> Our dataset names mapping
    # Note: GADM sometimes uses shortened names (e.g., "Jihočeský" instead of "Jihočeský kraj")
    gadm_to_dataset = {
        # Full names
        'Praha': 'Prague',
        'Prague': 'Prague',
        'Středočeský kraj': 'Central Bohemia',
        'Středočeský': 'Central Bohemia',
        'Jihočeský kraj': 'South Bohemia',
        'Jihočeský': 'South Bohemia',
        'Plzeňský kraj': 'Plzen',
        'Plzeňský': 'Plzen',
        'Karlovarský kraj': 'Karlovy Vary',
        'Karlovarský': 'Karlovy Vary',
        'Ústecký kraj': 'Usti nad Labem',
        'Ústecký': 'Usti nad Labem',
        'Liberecký kraj': 'Liberec',
        'Liberecký': 'Liberec',
        'Královéhradecký kraj': 'Hradec Kralove',
        'Královéhradecký': 'Hradec Kralove',
        'Pardubický kraj': 'Pardubice',
        'Pardubický': 'Pardubice',
        'Kraj Vysočina': 'Vysocina',
        'Vysočina': 'Vysocina',
        'Jihomoravský kraj': 'South Moravia',
        'Jihomoravský': 'South Moravia',
        'Olomoucký kraj': 'Olomouc',
        'Olomoucký': 'Olomouc',
        'Zlínský kraj': 'Zlin',
        'Zlínský': 'Zlin',
        'Moravskoslezský kraj': 'Moravia-Silesia',
        'Moravskoslezský': 'Moravia-Silesia'
    }
    
    # Reverse mapping (dataset -> GADM)
    dataset_to_gadm = {v: k for k, v in gadm_to_dataset.items()}
    
    # Try direct match first
    if region_name in gadm_to_dataset:
        return gadm_to_dataset[region_name]
    if region_name in dataset_to_gadm:
        return region_name  # Already in dataset format
    
    # Try case-insensitive and partial matching
    region_lower = region_name.lower()
    for gadm_name, dataset_name in gadm_to_dataset.items():
        if gadm_name.lower() == region_lower or dataset_name.lower() == region_lower:
            return dataset_name
    
    # Common variations
    variations = {
        'Prague': 'Prague',
        'Praha': 'Prague',
        'Hlavní město Praha': 'Prague',
        'Central Bohemia': 'Central Bohemia',
        'Středočeský kraj': 'Central Bohemia',
        'Stredocesky': 'Central Bohemia',
        'South Bohemia': 'South Bohemia',
        'Jihočeský kraj': 'South Bohemia',
        'Jihocesky': 'South Bohemia',
        'Plzen': 'Plzen',
        'Plzeňský kraj': 'Plzen',
        'Plzeň': 'Plzen',
        'Karlovy Vary': 'Karlovy Vary',
        'Karlovarský kraj': 'Karlovy Vary',
        'Usti nad Labem': 'Usti nad Labem',
        'Ústecký kraj': 'Usti nad Labem',
        'Ústí nad Labem': 'Usti nad Labem',
        'Liberec': 'Liberec',
        'Liberecký kraj': 'Liberec',
        'Hradec Kralove': 'Hradec Kralove',
        'Královéhradecký kraj': 'Hradec Kralove',
        'Hradec Králové': 'Hradec Kralove',
        'Pardubice': 'Pardubice',
        'Pardubický kraj': 'Pardubice',
        'Vysocina': 'Vysocina',
        'Kraj Vysočina': 'Vysocina',
        'Vysočina': 'Vysocina',
        'South Moravia': 'South Moravia',
        'Jihomoravský kraj': 'South Moravia',
        'Jihomoravsky': 'South Moravia',
        'Olomouc': 'Olomouc',
        'Olomoucký kraj': 'Olomouc',
        'Zlin': 'Zlin',
        'Zlínský kraj': 'Zlin',
        'Zlín': 'Zlin',
        'Moravia-Silesia': 'Moravia-Silesia',
        'Moravskoslezský kraj': 'Moravia-Silesia',
        'Moravskoslezsky': 'Moravia-Silesia'
    }
    
    return variations.get(region_name, region_name)

# python

