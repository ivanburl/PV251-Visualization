import dash
import pandas as pd
from dash import html, dcc, Output, Input, callback, State

# Import views
from components.dashboard_views.charts_view import render_charts_view
from components.dashboard_views.filters_view import render_filters_view, render_content
from components.dashboard_views.map_view import render_map_view
from components.dashboard_views.regional_view import render_regional_view

# Import IDs
from components.ids import ROAD_TYPE_CHART, COLLISION_CHART, CAR_BRAND_CHART, SANKEY_CHART, FILTER_REGION, FILTER_DATE, \
  FILTER_WEATHER, FILTER_ROAD_TYPE, FILTER_ACCIDENT_TYPE, FILTER_VEHICLE_TYPE, FILTER_AGE, FILTER_RESET, \
  SELECTED_REGION_STORAGE, MAP_VIEW_MODE_STORAGE, FILTER_SHOW_INDIVIDUAL, REGIONAL_DETAILS, \
  MAP_CLUSTERING_LAYER, MAP_REGIONAL_LAYER

from utils.create_charts import create_road_type_chart, create_collision_chart, create_car_brand_chart, \
  create_sankey_diagram, normalize_region_name, get_geojson_region, get_geojson_cluster
from utils.data_processing import load_and_process_data, get_filtered_data
from utils.utils import load_geojson

print("Loading data...")
df = load_and_process_data()
print(f"Data loaded: {len(df)} records")
print(f"Columns: {df.columns.tolist()}")
print(f"Sample data:\n{df.head()}")

# Extract unique values for filter dropdowns
regions = sorted([r for r in df['region'].unique() if pd.notna(r)])
road_types = sorted([r for r in df['road_type'].unique() if pd.notna(r)])
accident_types = sorted([r for r in df['accident_type'].unique() if pd.notna(r)])
vehicle_types = sorted([r for r in df['vehicle_type'].unique() if pd.notna(r)])
weather_conditions = sorted([w for w in df['weather'].unique() if pd.notna(w)])

dash.register_page(__name__, path='/', name="Dashboard")

layout = html.Div(
  className="flex flex-col h-dvh w-full lg:overflow-y-none",
  children=[
    html.Div(
      className="relative w-full flex-grow min-h-0 h-full flex flex-col overflow-y-auto lg:overflow-hidden lg:grid lg:grid-cols-12",
      children=[
        render_filters_view(df, regions, weather_conditions, road_types, accident_types, vehicle_types),
        render_map_view(),
        render_charts_view()
      ],
    ),

    # Client-side storage for a selected region (used for drill-down)
    dcc.Store(id=SELECTED_REGION_STORAGE, data=None),
    # Client-side storage for map view mode ('region' or 'individual')
    dcc.Store(id=MAP_VIEW_MODE_STORAGE, data='region')
  ]
)


# Callback: Reset all filters to default values

@callback(
  [Output(FILTER_REGION, 'value'),
   Output(FILTER_DATE, 'start_date'),
   Output(FILTER_DATE, 'end_date'),
   Output(FILTER_WEATHER, 'value'),
   Output(FILTER_ROAD_TYPE, 'value'),
   Output(FILTER_ACCIDENT_TYPE, 'value'),
   Output(FILTER_VEHICLE_TYPE, 'value'),
   Output(FILTER_AGE, 'value'),
   Output(SELECTED_REGION_STORAGE, 'data')],
  [Input(FILTER_RESET, 'n_clicks')],
  prevent_initial_call=True
)
def reset_filters(n_clicks):
  # Reset all filters when button clicked
  if n_clicks > 0:
    return ('all',
            df['date'].min() if 'date' in df.columns and df['date'].notna().any() else None,
            df['date'].max() if 'date' in df.columns and df['date'].notna().any() else None,
            'all', 'all', 'all', 'all',
            [int(df['age'].min()) if 'age' in df.columns and df['age'].notna().any() else 18,
             int(df['age'].max()) if 'age' in df.columns and df['age'].notna().any() else 80],
            None)
  return dash.no_update





# Callback: Update map view mode based on checkbox state
@callback(
  Output(MAP_VIEW_MODE_STORAGE, 'data'),
  [Input(FILTER_SHOW_INDIVIDUAL, 'checked')]
)
def update_map_view_mode(show_individual):
  # Returns 'individual' if checked, 'region' otherwise
  return 'individual' if show_individual else 'region'

@callback(
    Output('filters-view', 'children'),
    Input('screen-size', 'data'),
    prevent_initial_call=True
)
def update_filters_view(screen_size):
    is_mobile = screen_size['is_mobile']
    return [render_content(is_mobile,df, regions, weather_conditions,road_types, accident_types, vehicle_types)]


# Main callback: Updates all visualizations when filters change
# All charts and map update simultaneously (global linking)
@callback(
  [Output(ROAD_TYPE_CHART, 'spec'),
   Output(COLLISION_CHART, 'spec'),
   Output(CAR_BRAND_CHART, 'spec'),
   Output(SANKEY_CHART, 'figure'),
   Output(REGIONAL_DETAILS, 'children'),
   Output(MAP_REGIONAL_LAYER,"data"),
   Output(MAP_CLUSTERING_LAYER,"data")
  ],
  [Input(FILTER_REGION, 'value'),
   Input(FILTER_DATE, 'value'),
   Input(FILTER_WEATHER, 'value'),
   Input(FILTER_ROAD_TYPE, 'value'),
   Input(FILTER_ACCIDENT_TYPE, 'value'),
   Input(FILTER_VEHICLE_TYPE, 'value'),
   Input(FILTER_AGE, 'value'),
   Input(SELECTED_REGION_STORAGE, 'data'),
   Input(MAP_VIEW_MODE_STORAGE, 'data')]
)
def update_dashboard(region, date_range, weather, road_type, accident_type,
                     vehicle_type, age_range, selected_region, map_view_mode):
  selected_region = normalize_region_name(selected_region)
  
  show_individual = (map_view_mode == 'individual')

  filtered_df = get_filtered_data(df, region, date_range[0], date_range[1], weather,
                                  road_type, accident_type, vehicle_type, age_range, selected_region)

  geojson_cluster = None
  regional_details = html.Div()

  if selected_region:
    # Calculate statistics for a selected region
    # filtered_df is already filtered by selected_region
    region_data = filtered_df
    region_length = len(region_data)
    if region_length > 0:
      total_accidents = region_length
      fatalities = region_data['severity'].value_counts().get('Fatal', 0)
      serious = region_data['severity'].value_counts().get('Serious', 0)
      slight = region_data['severity'].value_counts().get('Slight', 0)
      avg_age = region_data['age'].mean() if 'age' in region_data.columns and region_data['age'].notna().any() else None
      top_road_type = region_data['road_type'].mode()[0] if len(region_data['road_type'].mode()) > 0 else 'N/A'
      top_brand = region_data['car_brand'].mode()[0] if 'car_brand' in region_data.columns and len(
        region_data['car_brand'].mode()) > 0 else 'N/A'
      if not show_individual:
        regional_details = render_regional_view(selected_region, total_accidents, fatalities, serious, slight, avg_age,
                                              top_road_type, top_brand)


  # Create update to GeoJSON to add density
  if not show_individual:
    # We need data filtered by dropdowns but NOT by map selection (to show context on map)
    if selected_region:
         filtered_without_region = get_filtered_data(df, region, date_range[0], date_range[1], weather,
                                                road_type, accident_type, vehicle_type, age_range, None)
    else:
         filtered_without_region = filtered_df
         
    geojson_region = get_geojson_region(filtered_without_region)
  else:
    # If showing individual, we need the base geojson for the map layer
    geojson_region = load_geojson()
    geojson_cluster = get_geojson_cluster(filtered_df)

  # Create all visualizations with filtered data
  road_type_fig = create_road_type_chart(filtered_df)
  collision_fig = create_collision_chart(filtered_df)
  car_brand_fig = create_car_brand_chart(filtered_df)
  sankey_fig = create_sankey_diagram(filtered_df)

  return (
    road_type_fig.to_dict(), collision_fig.to_dict(), car_brand_fig.to_dict(), sankey_fig,regional_details,geojson_region, geojson_cluster
   )
