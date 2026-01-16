"""
Data loading and processing functions for Czechia Road Safety Dashboard
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def load_and_process_data(data_path=None):
    """
    Load and process accident data from CSV file(s)
    Args:
        data_path: Path to CSV file or directory (None = auto-detect)
    Returns:
        Processed DataFrame with standardized columns
    """
    # Auto-detect data file if path not provided
    if data_path is None:
        # Check these paths in order (add more paths if needed)
        possible_paths = [
            'data/accidents.csv',
            'data/nehodovost.csv',
            'accidents.csv',
            'nehodovost.csv'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        # Create sample data if no file found
        if data_path is None or not os.path.exists(data_path):
            print("Warning: No data file found. Creating sample data structure.")
            print("Please download data from: https://policie.gov.cz/clanek/statistika-nehodovosti.aspx")
            return create_sample_data()
    
    # Load data
    try:
        if os.path.isdir(data_path):
            # Load all CSV files in directory
            csv_files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
            if len(csv_files) == 0:
                print("No CSV files found in data directory. Creating sample data...")
                return create_sample_data()
            dfs = []
            for file in csv_files:
                try:
                    # Try with error_bad_lines for older pandas, on_bad_lines for newer
                    try:
                        df_temp = pd.read_csv(os.path.join(data_path, file), encoding='utf-8', low_memory=False, on_bad_lines='skip')
                    except TypeError:
                        df_temp = pd.read_csv(os.path.join(data_path, file), encoding='utf-8', low_memory=False, error_bad_lines=False)
                    if len(df_temp) > 0:
                        dfs.append(df_temp)
                        print(f"Loaded {len(df_temp)} records from {file}")
                except Exception as e:
                    print(f"Warning: Could not load {file}: {e}")
                    continue
            if len(dfs) == 0:
                print("No valid data loaded. Creating sample data...")
                return create_sample_data()
            df = pd.concat(dfs, ignore_index=True)
            print(f"Total records loaded: {len(df)}")
        else:
            try:
                df = pd.read_csv(data_path, encoding='utf-8', low_memory=False, on_bad_lines='skip')
            except TypeError:
                df = pd.read_csv(data_path, encoding='utf-8', low_memory=False, error_bad_lines=False)
            print(f"Loaded {len(df)} records from {data_path}")
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Creating sample data structure...")
        return create_sample_data()
    
    # Process and standardize column names
    df = standardize_columns(df)
    
    # Clean and process data
    df = clean_data(df)
    
    return df

def standardize_columns(df):
    """
    Convert Czech column names to English standard names
    Add more mappings here if your data uses different column names
    """
    # Column name mapping: Czech/alternative names -> Standard English names
    # Add new mappings here for different data formats
    column_mapping = {
        # Region/Location
        'kraj': 'region',
        'Kraj': 'region',
        'REGION': 'region',
        'okres': 'region',
        'Okres': 'region',
        
        # Coordinates
        'latitude': 'lat',
        'Latitude': 'lat',
        'lat': 'lat',
        'longitude': 'lon',
        'Longitude': 'lon',
        'lon': 'lon',
        'lng': 'lon',
        'x': 'lon',
        'y': 'lat',
        
        # Date
        'datum': 'date',
        'Datum': 'date',
        'date': 'date',
        'DATE': 'date',
        'datum_nehody': 'date',
        
        # Road Type
        'druh_komunikace': 'road_type',
        'Druh komunikace': 'road_type',
        'road_type': 'road_type',
        'ROAD_TYPE': 'road_type',
        
        # Accident Type
        'druh_nehody': 'accident_type',
        'Druh nehody': 'accident_type',
        'accident_type': 'accident_type',
        'ACCIDENT_TYPE': 'accident_type',
        'typ_nehody': 'accident_type',
        
        # Collision Type
        'typ_kolize': 'collision_type',
        'Typ kolize': 'collision_type',
        'collision_type': 'collision_type',
        'COLLISION_TYPE': 'collision_type',
        
        # Severity
        'nasledky': 'severity',
        'Nasledky': 'severity',
        'severity': 'severity',
        'SEVERITY': 'severity',
        'vaznost': 'severity',
        
        # Weather
        'pocasi': 'weather',
        'Pocasi': 'weather',
        'weather': 'weather',
        'WEATHER': 'weather',
        'povetrnostni_podminky': 'weather',
        
        # Vehicle Type
        'druh_vozidla': 'vehicle_type',
        'Druh vozidla': 'vehicle_type',
        'vehicle_type': 'vehicle_type',
        'VEHICLE_TYPE': 'vehicle_type',
        
        # Car Brand
        'znacka': 'car_brand',
        'Znacka': 'car_brand',
        'car_brand': 'car_brand',
        'CAR_BRAND': 'car_brand',
        'znacka_vozidla': 'car_brand',
        
        # Age
        'vek': 'age',
        'Vek': 'age',
        'age': 'age',
        'AGE': 'age',
        'vek_ridice': 'age',
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    return df

def clean_data(df):
    """
    Clean and validate data: create missing columns, standardize values, filter invalid data
    """
    # Create missing columns with None values
    required_columns = ['region', 'lat', 'lon', 'date', 'road_type', 'accident_type',
                       'collision_type', 'severity', 'weather', 'vehicle_type', 'car_brand', 'age']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Convert date to datetime format
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Standardize severity values: map variations to standard names
    # Add more mappings here if your data uses different severity labels
    if 'severity' in df.columns:
        severity_mapping = {
            'slight': 'Slight',
            'Slight': 'Slight',
            'serious': 'Serious',
            'Serious': 'Serious',
            'fatal': 'Fatal',
            'Fatal': 'Fatal',
            'smrtelna': 'Fatal',  # Czech: fatal
            'tezka': 'Serious',   # Czech: serious
            'lehka': 'Slight'     # Czech: slight
        }
        df['severity'] = df['severity'].map(severity_mapping).fillna(df['severity'])
    
    # Convert coordinates to numeric
    if 'lat' in df.columns:
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    if 'lon' in df.columns:
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    
    # Filter to Czechia bounds: remove records outside country
    # Adjust bounds if needed: lat (south to north), lon (west to east)
    if 'lat' in df.columns and 'lon' in df.columns:
        df = df[(df['lat'] >= 48.5) & (df['lat'] <= 51.1) &
                (df['lon'] >= 12.0) & (df['lon'] <= 18.9)]
    
    # Validate age: must be numeric and reasonable (18+)
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df = df[(df['age'] >= 18) | df['age'].isna()]  # Keep valid ages or NaN
    
    return df

def get_filtered_data(df, region='all', start_date=None, end_date=None, weather='all',
                     road_type='all', accident_type='all', vehicle_type='all',
                     age_range=None, selected_region=None):
    """
    Apply all active filters to dataset
    Args:
        df: Original DataFrame
        region: Filter region ('all' = no filter)
        start_date: Filter start date (None = no filter)
        end_date: Filter end date (None = no filter)
        weather: Filter weather ('all' = no filter)
        road_type: Filter road type ('all' = no filter)
        accident_type: Filter accident type ('all' = no filter)
        vehicle_type: Filter vehicle type ('all' = no filter)
        age_range: [min_age, max_age] or None (None = no filter)
        selected_region: Region from map click (takes precedence over region filter)
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Region filter: map selection overrides dropdown selection
    if selected_region:
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    elif region != 'all':
        filtered_df = filtered_df[filtered_df['region'] == region]
    
    # Date range filter: keep records within date range
    if start_date and 'date' in filtered_df.columns:
        start_date = pd.to_datetime(start_date)
        filtered_df = filtered_df[filtered_df['date'] >= start_date]
    
    if end_date and 'date' in filtered_df.columns:
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[filtered_df['date'] <= end_date]
    
    # Weather filter: exact match
    if weather != 'all' and 'weather' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['weather'] == weather]
    
    # Road type filter: exact match
    if road_type != 'all' and 'road_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['road_type'] == road_type]
    
    # Accident type filter: exact match
    if accident_type != 'all' and 'accident_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['accident_type'] == accident_type]
    
    # Vehicle type filter: exact match
    if vehicle_type != 'all' and 'vehicle_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['vehicle_type'] == vehicle_type]
    
    # Age range filter: keep records with age in range (or NaN)
    if age_range and 'age' in filtered_df.columns:
        min_age, max_age = age_range
        filtered_df = filtered_df[((filtered_df['age'] >= min_age) & 
                                  (filtered_df['age'] <= max_age)) | 
                                  filtered_df['age'].isna()]
    
    return filtered_df

def create_sample_data():
    """
    Generate sample data when no CSV file is found
    Change n_samples to generate more/fewer records
    """
    np.random.seed(42)  # Random seed for reproducibility (change for different data)
    n_samples = 5000  # Number of sample records (change to adjust dataset size)
    
    # Czech regions with approximate center coordinates
    # Add/modify regions here if needed
    regions_data = {
        'Prague': {'lat': 50.0755, 'lon': 14.4378, 'weight': 0.15},
        'Central Bohemia': {'lat': 50.0, 'lon': 14.5, 'weight': 0.12},
        'South Bohemia': {'lat': 49.0, 'lon': 14.5, 'weight': 0.08},
        'Plzen': {'lat': 49.7475, 'lon': 13.3775, 'weight': 0.08},
        'Karlovy Vary': {'lat': 50.2304, 'lon': 12.8721, 'weight': 0.05},
        'Usti nad Labem': {'lat': 50.6611, 'lon': 14.0531, 'weight': 0.10},
        'Liberec': {'lat': 50.7663, 'lon': 15.0543, 'weight': 0.07},
        'Hradec Kralove': {'lat': 50.2092, 'lon': 15.8328, 'weight': 0.08},
        'Pardubice': {'lat': 50.0344, 'lon': 15.7819, 'weight': 0.07},
        'Vysocina': {'lat': 49.3967, 'lon': 15.5903, 'weight': 0.06},
        'South Moravia': {'lat': 49.1951, 'lon': 16.6068, 'weight': 0.10},
        'Olomouc': {'lat': 49.5938, 'lon': 17.2509, 'weight': 0.07},
        'Zlin': {'lat': 49.2264, 'lon': 17.6700, 'weight': 0.05},
        'Moravia-Silesia': {'lat': 49.8209, 'lon': 18.2625, 'weight': 0.12}
    }
    
    regions = list(regions_data.keys())
    region_weights = [regions_data[r]['weight'] for r in regions]
    # Normalize weights to sum to 1
    total_weight = sum(region_weights)
    region_weights = [w / total_weight for w in region_weights]
    
    # Generate data with regional clustering
    data_list = []
    for i in range(n_samples):
        region = np.random.choice(regions, p=region_weights)
        region_info = regions_data[region]
        # Add some random variation around region center
        lat = region_info['lat'] + np.random.normal(0, 0.3)
        lon = region_info['lon'] + np.random.normal(0, 0.3)
        
        # Ensure within Czechia bounds
        lat = np.clip(lat, 48.5, 51.1)
        lon = np.clip(lon, 12.0, 18.9)
        
        data_list.append({
            'region': region,
            'lat': lat,
            'lon': lon,
            'date': pd.Timestamp('2020-01-01') + pd.Timedelta(days=np.random.randint(0, 1825)),  # 5 years
            'road_type': np.random.choice(['Highway', 'Main Road', 'Local Road', 'City Street'], 
                                         p=[0.15, 0.35, 0.30, 0.20]),
            'accident_type': np.random.choice(['Collision', 'Run-off', 'Pedestrian', 'Other'], 
                                             p=[0.50, 0.25, 0.15, 0.10]),
            'collision_type': np.random.choice(['Frontal', 'Rear', 'Side', 'Single'], 
                                              p=[0.20, 0.30, 0.35, 0.15]),
            'severity': np.random.choice(['Slight', 'Serious', 'Fatal'], 
                                        p=[0.75, 0.20, 0.05]),
            'weather': np.random.choice(['Clear', 'Rain', 'Snow', 'Fog'], 
                                      p=[0.60, 0.25, 0.10, 0.05]),
            'vehicle_type': np.random.choice(['Car', 'Truck', 'Motorcycle', 'Bus'], 
                                            p=[0.75, 0.12, 0.10, 0.03]),
            'car_brand': np.random.choice(['Skoda', 'VW', 'BMW', 'Audi', 'Ford', 'Renault', 'Hyundai', 'Toyota'], 
                                         p=[0.30, 0.20, 0.12, 0.10, 0.08, 0.08, 0.06, 0.06]),
            'age': np.random.randint(18, 80)
        })
    
    df = pd.DataFrame(data_list)
    return df

