# Czechia Road Safety Dashboard

An interactive web dashboard for exploring and analyzing road traffic accident data in the Czech Republic.

## Overview

This dashboard provides comprehensive analysis of road safety data in Czechia, featuring:

- **Interactive Map**: Visualize accident hotspots and clusters across Czechia
- **Multi-dimensional Filtering**: Filter by region, date, weather, road type, accident type, vehicle type, and age
- **Linked Visualizations**: All charts update simultaneously based on filter selections
- **Drill-down Analysis**: Click on map regions to see detailed regional statistics
- **Comprehensive Charts**: 
  - Road Type Bar Chart
  - Collision Type Pie Chart
  - Car Brand Safety Analysis
  - Sankey Diagram (Collision Type → Severity Flow)

## Features

### Interactive Features

1. **Global Filtering**: All filters in the left panel update the entire dashboard instantly
2. **Map Interactions**:
   - Hover over accident clusters to see detailed statistics
   - Click on regions to drill down and filter all charts
   - Zoom controls for detailed geographical analysis
3. **Chart Interactions**: Hover over any chart element to see precise values
4. **Regional Details Panel**: Appears below the map when a region is selected, showing:
   - Total accidents
   - Severity breakdown (Fatal, Serious, Slight)
   - Average driver age
   - Most common road types
   - Top car brands

## Data Source

Data should be obtained from the Czech Police website:
https://policie.gov.cz/clanek/statistika-nehodovosti.aspx

**Note**: The dataset contains data up to 2025 and includes:
- High variety of enumerations
- Many NaN values (due to high diversity of accidents)
- Requires filtering and cleaning

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd VIS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download data from the Czech Police website and place CSV file(s) in the `data/` directory

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:8050`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t czechia-road-safety .
```

2. Run the container:
```bash
docker run -p 8050:8050 -v $(pwd)/data:/app/data czechia-road-safety
```

3. Access the dashboard at `http://localhost:8050`

### Cloud Deployment

The application can be deployed to cloud platforms like:
- Oracle Cloud Infrastructure
- Microsoft Azure
- AWS

Use the provided Dockerfile for containerized deployment.

## Project Structure

```
VIS/
├── app.py                 # Main Dash application
├── data_processing.py     # Data loading and cleaning functions
├── utils.py               # Visualization utility functions
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── README.md             # This file
└── data/                 # Data directory (place CSV files here)
    └── accidents.csv      # Accident data file(s)
```

## Data Format

The application expects CSV files with the following columns (or Czech equivalents):

- `region` / `kraj`: Region name
- `lat` / `latitude`: Latitude coordinate
- `lon` / `longitude`: Longitude coordinate
- `date` / `datum`: Date of accident
- `road_type` / `druh_komunikace`: Type of road
- `accident_type` / `druh_nehody`: Type of accident
- `collision_type` / `typ_kolize`: Type of collision
- `severity` / `nasledky`: Severity (Slight, Serious, Fatal)
- `weather` / `pocasi`: Weather conditions
- `vehicle_type` / `druh_vozidla`: Type of vehicle
- `car_brand` / `znacka`: Car brand
- `age` / `vek`: Driver age

The application automatically handles various column name formats and standardizes them.

## Technologies

- **Python 3.11+**: Core programming language
- **Dash**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data processing and manipulation
- **NumPy**: Numerical computations
- **Docker**: Containerization
- **Gunicorn**: Production WSGI server

## Design Principles

- **Clean, Modern UI**: Light-mode interface with subtle grey backgrounds
- **Color Coding**: 
  - Sequential yellow-to-red palette for severity and density
  - Colorblind-safe categorical colors for different data types
  - Bright accent colors for active filters and selections
- **User-Driven Exploration**: Extensive filtering and tightly linked visualizations
- **Responsive Design**: Adapts to different screen sizes

## Usage

1. **Filter Data**: Use the left panel to filter by various criteria
2. **Explore Map**: Hover over accident clusters to see statistics
3. **Drill Down**: Click on a region to see detailed regional analysis
4. **Analyze Charts**: All charts update automatically based on your filters
5. **Reset**: Click "Reset Filters" to return to the full dataset

## Authors

- Muhammed Selimcan Bicer (579427)
- Ivan Burlutskyi (532094)
- Lucas Beranger (579422)

## License

This project is for educational purposes.

## Notes

- If no data file is found, the application will create sample data for demonstration
- The application handles missing values (NaN) gracefully
- All visualizations are interactive and linked
- Regional drill-down provides context-aware filtering

