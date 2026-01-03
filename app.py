"""
Czechia Road Safety Dashboard
Main Dash application for interactive road accident analysis
"""

import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from data_processing import load_and_process_data, get_filtered_data
from utils import create_map, create_road_type_chart, create_collision_chart, create_car_brand_chart, create_sankey_diagram

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Czechia Road Safety Dashboard"  # Browser tab title

# Custom HTML template for consistent font rendering
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load and process data
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

# App layout - 3-column design: Filters (20%) | Map (45%) | Charts (35%)
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Czechia Road Safety Dashboard", 
                style={'textAlign': 'center', 'margin': '0', 'color': '#2c3e50', 
                       'fontSize': '32px', 'fontWeight': 'bold', 'padding': '20px 0 10px 0'}),
        html.P("Comprehensive Czechia Road Safety Analysis", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'margin': '0', 'fontSize': '16px', 'paddingBottom': '15px'})
    ], style={'backgroundColor': '#ecf0f1', 'width': '100%'}),
    
    # Main content: 3-column layout
    html.Div([
        # LEFT PANEL: Filters (20% width - change 'width' value to adjust)
        html.Div([
            html.H3("Filters", style={
                'marginBottom': '20px', 
                'color': '#34495e', 
                'fontSize': '20px',  # Header font size
                'borderBottom': '2px solid #bdc3c7', 
                'paddingBottom': '12px',
                'fontWeight': 'bold'
            }),
            
            # Map view toggle: switches between region choropleth and individual accident bubbles
            html.Label("Map View:", style={'fontWeight': 'bold', 'marginTop': '0px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '10px'}),
            html.Div([
                dcc.Checklist(
                    id='show-individual',
                    options=[{'label': ' Show Individual Accidents', 'value': 'individual'}],
                    value=[],  # Default: unchecked (region view)
                    style={'fontSize': '14px', 'color': '#34495e'}
                )
            ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': 'white', 'borderRadius': '5px'}),
            
            html.Hr(style={'margin': '20px 0', 'borderColor': '#bdc3c7'}),
            
            html.Label("Region:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filter-region',
                options=[{'label': 'All Regions', 'value': 'all'}] + [{'label': r, 'value': r} for r in regions],
                value='all',
                clearable=False,
                style={'marginBottom': '20px', 'backgroundColor': 'white'}
            ),
            
            html.Label("Date Range:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '5px'}),
            dcc.DatePickerRange(
                id='filter-date',
                start_date=df['date'].min() if 'date' in df.columns and df['date'].notna().any() else None,
                end_date=df['date'].max() if 'date' in df.columns and df['date'].notna().any() else None,
                display_format='YYYY-MM-DD',
                style={'marginBottom': '20px', 'backgroundColor': 'white'}
            ),
            
            html.Label("Weather:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filter-weather',
                options=[{'label': 'All Weather', 'value': 'all'}] + [{'label': w, 'value': w} for w in weather_conditions],
                value='all',
                clearable=False,
                style={'marginBottom': '20px', 'backgroundColor': 'white'}
            ),
            
            html.Label("Road Type:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filter-road-type',
                options=[{'label': 'All Road Types', 'value': 'all'}] + [{'label': r, 'value': r} for r in road_types],
                value='all',
                clearable=False,
                style={'marginBottom': '20px', 'backgroundColor': 'white'}
            ),
            
            html.Label("Accident Type:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filter-accident-type',
                options=[{'label': 'All Types', 'value': 'all'}] + [{'label': a, 'value': a} for a in accident_types],
                value='all',
                clearable=False,
                style={'marginBottom': '20px', 'backgroundColor': 'white'}
            ),
            
            html.Label("Vehicle Type:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='filter-vehicle-type',
                options=[{'label': 'All Vehicles', 'value': 'all'}] + [{'label': v, 'value': v} for v in vehicle_types],
                value='all',
                clearable=False,
                style={'marginBottom': '20px', 'backgroundColor': 'white'}
            ),
            
            html.Label("Age Range:", style={'fontWeight': 'bold', 'marginTop': '15px', 'display': 'block', 'color': '#2c3e50'}),
            html.Div([
                dcc.RangeSlider(
                    id='filter-age',
                    min=int(df['age'].min()) if 'age' in df.columns and df['age'].notna().any() else 18,
                    max=int(df['age'].max()) if 'age' in df.columns and df['age'].notna().any() else 80,
                    value=[int(df['age'].min()) if 'age' in df.columns and df['age'].notna().any() else 18,
                           int(df['age'].max()) if 'age' in df.columns and df['age'].notna().any() else 80],
                    marks={i: str(i) for i in range(18, 81, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'marginBottom': '25px'}),
            
            html.Button('Reset Filters', id='reset-filters', n_clicks=0,
                       style={
                           'width': '100%', 
                           'padding': '12px', 
                           'marginTop': '25px',
                           'backgroundColor': '#e74c3c', 
                           'color': 'white', 
                           'border': 'none',
                           'borderRadius': '5px', 
                           'cursor': 'pointer', 
                           'fontSize': '16px',
                           'fontWeight': 'bold',
                           'transition': 'background-color 0.3s'
                       })
            
        ], style={
            'width': '20%',  # Panel width (change to adjust left panel size)
            'float': 'left', 
            'padding': '20px',  # Internal padding
            'backgroundColor': '#ecf0f1',  # Panel background color
            'height': 'calc(100vh - 120px)',  # Height: viewport height minus header
            'overflowY': 'auto',  # Enable vertical scrolling if content overflows
            'boxShadow': '2px 0 8px rgba(0,0,0,0.1)'  # Right-side shadow
        }),
        
        # CENTER PANEL: Map (45% width - change 'width' value to adjust)
        html.Div([
            html.Div([
                html.H4("Czechia Map - Accident Hotspots", style={
                    'marginBottom': '15px', 
                    'color': '#2c3e50', 
                    'fontSize': '18px',  # Map title font size
                    'fontWeight': 'bold'
                }),
                dcc.Graph(
                    id='map-plot',  # Map visualization (choropleth or scatter)
                    style={
                        'height': 'calc(100vh - 250px)',  # Map height: viewport minus header and title
                        'borderRadius': '8px',  # Rounded corners
                        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',  # Shadow effect
                        'backgroundColor': 'white'
                    }
                )
            ]),
            # Regional details panel: appears below map when region is clicked
            html.Div(
                id='regional-details',  # Populated by callback when region selected
                style={
                    'marginTop': '20px', 
                    'padding': '20px',
                    'backgroundColor': '#f8f9fa', 
                    'borderRadius': '8px',
                    'display': 'none',  # Hidden by default, shown when region clicked
                    'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
                }
            )
        ], style={
            'width': '45%',  # Panel width (change to adjust center panel size)
            'float': 'left', 
            'padding': '20px'
        }),
        
        # RIGHT PANEL: Analytics Charts (35% width - change 'width' value to adjust)
        html.Div([
            html.H4("Analytics Panel", style={
                'marginBottom': '20px', 
                'color': '#2c3e50', 
                'fontSize': '18px',  # Panel title font size
                'fontWeight': 'bold',
                'borderBottom': '2px solid #bdc3c7', 
                'paddingBottom': '12px'
            }),
            # Chart 1: Road Type Bar Chart
            html.Div([
                dcc.Graph(
                    id='road-type-chart', 
                    style={
                        'height': '280px',  # Chart height (change to adjust chart size)
                        'marginBottom': '20px',  # Space between charts
                        'borderRadius': '8px', 
                        'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                )
            ], style={'marginBottom': '20px'}),
            # Chart 2: Collision Types Pie Chart
            html.Div([
                dcc.Graph(
                    id='collision-chart', 
                    style={
                        'height': '280px',  # Chart height
                        'marginBottom': '20px',
                        'borderRadius': '8px', 
                        'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                )
            ], style={'marginBottom': '20px'}),
            # Chart 3: Car Brand Safety Bar Chart (stacked)
            html.Div([
                dcc.Graph(
                    id='car-brand-chart', 
                    style={
                        'height': '280px',  # Chart height
                        'marginBottom': '20px',
                        'borderRadius': '8px', 
                        'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                )
            ], style={'marginBottom': '20px'}),
            # Chart 4: Sankey Diagram (Collision Type → Severity flow)
            html.Div([
                dcc.Graph(
                    id='sankey-chart', 
                    style={
                        'height': '280px',  # Chart height
                        'borderRadius': '8px', 
                        'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
                        'backgroundColor': 'white'
                    }
                )
            ])
        ], style={
            'width': '35%',  # Panel width (change to adjust right panel size)
            'float': 'left', 
            'padding': '20px', 
            'height': 'calc(100vh - 120px)',  # Height: viewport height minus header
            'overflowY': 'auto',  # Enable scrolling for charts
            'boxSizing': 'border-box'
        })
    ], style={'display': 'flex', 'flexDirection': 'row', 'height': 'calc(100vh - 120px)'}),
    
    # Client-side storage for selected region (used for drill-down)
    dcc.Store(id='selected-region', data=None),
    # Client-side storage for map view mode ('region' or 'individual')
    dcc.Store(id='map-view-mode', data='region')
], style={'width': '100%', 'height': '100vh', 'margin': '0', 'padding': '0'})

# Callback: Reset all filters to default values
@app.callback(
    [Output('filter-region', 'value'),
     Output('filter-date', 'start_date'),
     Output('filter-date', 'end_date'),
     Output('filter-weather', 'value'),
     Output('filter-road-type', 'value'),
     Output('filter-accident-type', 'value'),
     Output('filter-vehicle-type', 'value'),
     Output('filter-age', 'value'),
     Output('selected-region', 'data')],
    [Input('reset-filters', 'n_clicks')],
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

# Callback: Handle map clicks to select/deselect regions for drill-down
@app.callback(
    Output('selected-region', 'data', allow_duplicate=True),
    [Input('map-plot', 'clickData')],
    [State('selected-region', 'data')],
    prevent_initial_call=True
)
def update_selected_region(click_data, current_selection):
    if click_data and click_data.get('points'):
        point = click_data['points'][0]
        
        # Choropleth maps: location contains GADM Czech name
        if 'location' in point:
            clicked_region_gadm = point['location']
            # Convert GADM name to dataset English name
            from utils import normalize_region_name
            clicked_region = normalize_region_name(clicked_region_gadm)
        else:
            # Scatter points: use customdata
            customdata = point.get('customdata')
            if isinstance(customdata, dict):
                clicked_region = customdata.get('region')
            elif isinstance(customdata, list) and len(customdata) > 0:
                if isinstance(customdata[0], dict):
                    clicked_region = customdata[0].get('region')
                else:
                    clicked_region = None
            else:
                clicked_region = None
        
        if clicked_region:
            # Toggle: click same region again to deselect
            if clicked_region == current_selection:
                return None
            return clicked_region
    return current_selection

# Callback: Update map view mode based on checkbox state
@app.callback(
    Output('map-view-mode', 'data'),
    [Input('show-individual', 'value')]
)
def update_map_view_mode(show_individual):
    # Returns 'individual' if checked, 'region' otherwise
    return 'individual' if show_individual and 'individual' in show_individual else 'region'

# Main callback: Updates all visualizations when filters change
# All charts and map update simultaneously (global linking)
@app.callback(
    [Output('map-plot', 'figure'),
     Output('road-type-chart', 'figure'),
     Output('collision-chart', 'figure'),
     Output('car-brand-chart', 'figure'),
     Output('sankey-chart', 'figure'),
     Output('regional-details', 'children'),
     Output('regional-details', 'style')],
    [Input('filter-region', 'value'),
     Input('filter-date', 'start_date'),
     Input('filter-date', 'end_date'),
     Input('filter-weather', 'value'),
     Input('filter-road-type', 'value'),
     Input('filter-accident-type', 'value'),
     Input('filter-vehicle-type', 'value'),
     Input('filter-age', 'value'),
     Input('selected-region', 'data'),
     Input('map-view-mode', 'data')]
)
def update_dashboard(region, start_date, end_date, weather, road_type, accident_type, 
                     vehicle_type, age_range, selected_region, map_view_mode):
    # Apply all filters to dataset
    filtered_df = get_filtered_data(df, region, start_date, end_date, weather, 
                                    road_type, accident_type, vehicle_type, age_range, selected_region)
    
    print(f"Filtered data: {len(filtered_df)} records")
    
    # Check if showing individual accidents or regions
    show_individual = (map_view_mode == 'individual')
    
    # Create all visualizations with filtered data
    map_fig = create_map(filtered_df, selected_region, show_individual=show_individual)
    road_type_fig = create_road_type_chart(filtered_df)
    collision_fig = create_collision_chart(filtered_df)
    car_brand_fig = create_car_brand_chart(filtered_df)
    sankey_fig = create_sankey_diagram(filtered_df)
    
    # Regional details panel: shown when region is clicked
    regional_details = None
    details_style = {
        'marginTop': '20px', 
        'padding': '20px',
        'backgroundColor': '#f8f9fa', 
        'borderRadius': '8px', 
        'display': 'none'  # Hidden by default
    }
    
    if selected_region:
        # Calculate statistics for selected region
        region_data = filtered_df[filtered_df['region'] == selected_region]
        if len(region_data) > 0:
            total_accidents = len(region_data)
            fatalities = region_data['severity'].value_counts().get('Fatal', 0)
            serious = region_data['severity'].value_counts().get('Serious', 0)
            slight = region_data['severity'].value_counts().get('Slight', 0)
            avg_age = region_data['age'].mean() if 'age' in region_data.columns and region_data['age'].notna().any() else None
            top_road_type = region_data['road_type'].mode()[0] if len(region_data['road_type'].mode()) > 0 else 'N/A'
            top_brand = region_data['car_brand'].mode()[0] if 'car_brand' in region_data.columns and len(region_data['car_brand'].mode()) > 0 else 'N/A'
            
            # Create details panel HTML
            regional_details = html.Div([
                html.H4(f"Regional Details: {selected_region}", style={
                    'color': '#2c3e50', 
                    'marginBottom': '15px',
                    'fontSize': '18px',  # Title font size
                    'fontWeight': 'bold'
                }),
                html.Div([
                    html.P([html.Strong("Total Accidents: "), f"{total_accidents:,}"], style={'margin': '8px 0', 'fontSize': '14px'}),
                    html.P([html.Strong("Fatal: "), f"{fatalities} ({fatalities/total_accidents*100:.1f}%)"], 
                           style={'margin': '8px 0', 'color': '#e74c3c', 'fontSize': '14px'}),
                    html.P([html.Strong("Serious: "), f"{serious} ({serious/total_accidents*100:.1f}%)"], 
                           style={'margin': '8px 0', 'color': '#e67e22', 'fontSize': '14px'}),
                    html.P([html.Strong("Slight: "), f"{slight} ({slight/total_accidents*100:.1f}%)"], 
                           style={'margin': '8px 0', 'color': '#f1c40f', 'fontSize': '14px'}),
                    html.P([html.Strong("Average Driver Age: "), f"{avg_age:.1f}" if avg_age else "N/A"], 
                           style={'margin': '8px 0', 'fontSize': '14px'}),
                    html.P([html.Strong("Most Common Road Type: "), top_road_type], style={'margin': '8px 0', 'fontSize': '14px'}),
                    html.P([html.Strong("Top Car Brand: "), top_brand], style={'margin': '8px 0', 'fontSize': '14px'})
                ])
            ])
            details_style['display'] = 'block'  # Show panel
    
    return map_fig, road_type_fig, collision_fig, car_brand_fig, sankey_fig, regional_details, details_style

# Expose server for gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
