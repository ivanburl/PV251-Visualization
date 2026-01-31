import os

import pandas as pd
from pyproj import Transformer


def process_folder(folder_path: str):
    """
    Process police data folder to create accidents.csv
    """
    print(f"Processing folder: {folder_path}")

    # Define file paths
    files = {
        'accidents': os.path.join(folder_path, 'Inehody.xls'),
        'vehicles': os.path.join(folder_path, 'Ivozidla.xls'),
        'persons': os.path.join(folder_path, 'Inasledky.xls'),
        'gps': os.path.join(folder_path, 'IntGPS.xls')
    }

    # Check existence
    if not all(os.path.exists(f) for f in files.values()):
        print(f"Missing required files in {folder_path}")
        return

    # Load data using pd.read_html
    # Load data using pd.read_html
    print("Loading data files...")
    # read_html returns a list of dataframes, we want the first one
    # Use converters to ensure IDs and key columns are read as strings
    str_converters = {'p1': str, 'id_vozidla': str}

    try:
        df_accidents = pd.read_html(files['accidents'], encoding='cp1250', converters=str_converters)[0]
        df_vehicles = pd.read_html(files['vehicles'], encoding='cp1250', converters=str_converters)[0]
        df_persons = pd.read_html(files['persons'], encoding='cp1250', converters=str_converters)[0]
        df_gps = pd.read_html(files['gps'], encoding='cp1250', converters=str_converters)[0]
    except Exception as e:
        print(f"Error reading files with pd.read_html: {e}")
        return

    # Filter for drivers only (p59a == '1')
    # Values are already strings due to converters
    df_drivers = df_persons[df_persons['p59a'] == 1].copy()

    print(f"Drivers found: {len(df_drivers)}")

    # Merge Data
    # 1. Drivers + Accidents (on p1) (Keys are already strings via converters)
    df_merged = pd.merge(df_drivers, df_accidents, on='p1', how='inner')

    # 2. + Vehicles (on p1 AND id_vozidla)
    df_merged = pd.merge(df_merged, df_vehicles, on=['p1', 'id_vozidla'], how='inner')

    # 3. + GPS (on p1)
    df_merged = pd.merge(df_merged, df_gps, on='p1', how='inner')

    df_merged['p59d'] = pd.to_numeric(df_merged['p59d'], errors='coerce')
    df_merged = df_merged.dropna(
        subset=['p4a', 'd', 'e', 'p2a', 'p36', 'p6', 'p7', 'p59g', 'p18', 'p44', 'p45a', 'p59d'])

    print(f"Merged records: {len(df_merged)}")

    region_type_map = {
        0: "Prague",
        1: "Central Bohemia",
        2: "South Bohemia",
        3: "Plzen",
        4: "Usti nad Labem",
        5: "Hradec Kralove",
        6: "South Moravia",
        7: "Moravia-Silesia",
        14: "Olomouc",
        15: "Zlin",
        16: "Vysocina",
        17: "Pardubice",
        18: "Liberec",
        19: "Karlovy Vary"
    }

    # p3 (Road Type)
    road_type_map = {
        0: 'Highway', 1: 'First Class Road', 2: 'Second Class Road', 3: 'Third Class Road',
        4: 'Intersection', 5: 'Monitored Road', 6: 'Local Road'
    }

    # p6 (Accident Type)
    accident_type_map = {
        1: 'Moving Vehicle Collision', 2: 'Parked Vehicle Collision', 3: 'Fixed Obstacle Collision',
        4: 'Pedestrian Collision', 5: 'Forest Animal Collision', 6: 'Domestic Animal Collision',
        7: 'Train Collision', 8: 'Tram Collision', 9: 'Crash'
    }

    # p7 (Collision Type)
    collision_type_map = {
        1: 'Frontal', 2: 'Side (Lateral)', 3: 'From Side (T-bone)', 4: 'Rear'
    }

    # p59g (Severity)
    severity_map = {
        1: 'Fatal', 2: 'Serious', 3: 'Slight'
    }

    # p18 (Weather)
    weather_map = {
        1: 'Good', 2: 'Fog', 3: 'Light Rain', 4: 'Rain', 5: 'Snow',
        6: 'Ice', 7: 'Wind'
    }

    # p44 (Vehicle Type)
    vehicle_type_map = {
        2: 'Motorcycle', 3: 'Car', 4: 'Car with Trailer', 5: 'Truck',
        6: 'Truck with Trailer', 7: 'Truck with Semi-trailer', 8: 'Bus',
        9: 'Tractor', 10: 'Tram', 11: 'Trolleybus', 12: 'Other Motor Vehicle',
        13: 'Bicycle', 16: 'Train', 18: 'Scooter/Other'
    }

    # p45a (Car Brand)
    car_brand_map = {
        1: 'ALFA-ROMEO', 2: 'AUDI', 3: 'AVIA', 4: 'BMW', 5: 'CHEVROLET',
        6: 'CHRYSLER', 7: 'CITROEN', 8: 'DACIA', 9: 'DAEWOO', 10: 'DAF',
        11: 'DODGE', 12: 'FIAT', 13: 'FORD', 14: 'GAZ, VOLHA', 15: 'FERRARI',
        16: 'HONDA', 17: 'HYUNDAI', 18: 'IFA', 19: 'IVECO', 20: 'JAGUAR',
        21: 'JEEP', 22: 'LANCIA', 23: 'LAND ROVER', 24: 'LIAZ', 25: 'MAZDA',
        26: 'MERCEDES', 27: 'MITSUBISHI', 28: 'MOSKVIČ', 29: 'NISSAN', 30: 'OLTCIT',
        31: 'OPEL', 32: 'PEUGEOT', 33: 'PORSCHE', 34: 'PRAGA', 35: 'RENAULT',
        36: 'ROVER', 37: 'SAAB', 38: 'SEAT', 39: 'ŠKODA', 40: 'SCANIA',
        41: 'SUBARU', 42: 'SUZUKI', 43: 'TATRA', 44: 'TOYOTA', 45: 'TRABANT',
        46: 'VAZ', 47: 'VOLKSWAGEN', 48: 'VOLVO', 49: 'WARTBURG', 50: 'ZASTAVA',
        51: 'AGM', 52: 'ARO', 53: 'AUSTIN', 54: 'BARKAS', 55: 'DAIHATSU',
        56: 'DATSUN', 57: 'DESTACAR', 58: 'ISUZU', 59: 'KAROSA', 60: 'KIA',
        61: 'LUBLIN', 62: 'MAN', 63: 'MASERATI', 64: 'MULTICAR', 65: 'PONTIAC',
        66: 'ROSS', 67: 'SIMCA', 68: 'SSANGYONG', 69: 'TALBOT', 70: 'TAZ',
        71: 'ZAZ', 72: 'BOVA', 73: 'IKARUS', 74: 'NEOPLAN', 75: 'OASA',
        76: 'RAF', 77: 'SETRA', 78: 'SOR', 79: 'APRILIA', 80: 'CAGIVA',
        81: 'ČZ', 82: 'DERBI', 83: 'DUCATI', 84: 'GILERA', 85: 'HARLEY',
        86: 'HERO', 87: 'HUSQVARNA', 88: 'JAWA', 89: 'KAWASAKI', 90: 'KTM',
        91: 'MALAGUTI', 92: 'MANET', 93: 'MZ', 94: 'PIAGGIO', 95: 'SIMSON',
        96: 'VELOREX', 97: 'YAMAHA'
    }

    # Map columns
    result_df = pd.DataFrame()
    result_df['region'] = df_merged['p4a'].map(region_type_map)

    df_merged = df_merged.dropna(subset=['e', 'd'])
    swapped = df_merged['d'] < df_merged['e']
    df_merged.loc[swapped, ['d', 'e']] = df_merged.loc[swapped, ['e', 'd']].values

    # 3. Initialize Transformer
    transformer = Transformer.from_crs("EPSG:5514", "EPSG:4326", always_xy=True)

    # 4. Transform
    # EPSG:5514 expects (Y, X) when always_xy=True
    result_df[['lon', 'lat']] = df_merged.apply(
        lambda row: transformer.transform(row['d'], row['e']),
        axis=1, result_type='expand'
    )
    result_df[['e', 'd']] = df_merged[['e', 'd']]

    result_df['date'] = df_merged['p2a']

    # Apply Mappings (Strict: NaNs for unmapped values)
    result_df['road_type'] = df_merged['p36'].map(road_type_map)
    result_df['accident_type'] = df_merged['p6'].map(accident_type_map)
    result_df['collision_type'] = df_merged['p7'].map(collision_type_map)
    result_df['severity'] = df_merged['p59g'].map(severity_map)
    result_df['weather'] = df_merged['p18'].map(weather_map)
    result_df['vehicle_type'] = df_merged['p44'].map(vehicle_type_map)
    result_df['car_brand'] = df_merged['p45a'].map(car_brand_map)

    result_df['age'] = df_merged['p59d'].astype(int)

    initial_count = len(result_df)
    result_df = result_df.dropna()
    final_count = len(result_df)
    print(f"Dropped {initial_count - final_count} rows with missing values.")

    return result_df



if __name__ == "__main__":

    years = [2023, 2024, 2025]

    frames = []
    for year in years:
        frames.append(process_folder(f"./data/police/{year}"))

    result_df = pd.concat(frames, ignore_index=True)

    result_df.to_csv("./data/accidents.csv", index = False)

