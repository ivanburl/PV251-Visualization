# Data Directory

Place your accident data CSV files in this directory.

## Data Source

Download data from the Czech Police website:
https://policie.gov.cz/clanek/statistika-nehodovosti.aspx

To fastly download and unpack the data you can use `donwload.sh` script. 
After completion of the `download.sh` script you can reproduce the accidents.csv file   
via the following command in root directory:

```bash
python ./utils/assembly_data.py
```

## Expected Format

The application can handle various column name formats. Common Czech column names that are automatically recognized:

- **Region**: `kraj`, `Kraj`, `okres`, `Okres`, `region`
- **Coordinates**: `latitude`, `lat`, `longitude`, `lon`, `lng`
- **Date**: `datum`, `Datum`, `datum_nehody`, `date`
- **Road Type**: `druh_komunikace`, `Druh komunikace`, `road_type`
- **Accident Type**: `druh_nehody`, `Druh nehody`, `accident_type`, `typ_nehody`
- **Collision Type**: `typ_kolize`, `Typ kolize`, `collision_type`
- **Severity**: `nasledky`, `Nasledky`, `severity`, `vaznost`
- **Weather**: `pocasi`, `Pocasi`, `weather`, `povetrnostni_podminky`
- **Vehicle Type**: `druh_vozidla`, `Druh vozidla`, `vehicle_type`
- **Car Brand**: `znacka`, `Znacka`, `car_brand`, `znacka_vozidla`
- **Age**: `vek`, `Vek`, `age`, `vek_ridice`

## File Naming

You can name your CSV file(s) anything, for example:
- `accidents.csv`
- `nehodovost.csv`
- `data_2020_2025.csv`

The application will automatically detect and load CSV files from this directory.

## Sample Data

If no data file is found, the application will create sample data for demonstration purposes.

