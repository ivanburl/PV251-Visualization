"""
Utility functions for creating visualizations
"""

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import os

# Color schemes matching PDF design
# Change colors here to modify severity color coding
SEVERITY_COLORS = {
    'Slight': '#f1c40f',  # Yellow
    'Serious': '#e67e22',  # Orange
    'Fatal': '#e74c3c'     # Red
}

# Sequential color palette for density visualization (yellow to red)
# Used for map density and severity encoding
DENSITY_COLORS = ['#fff9c4', '#fff59d', '#ffeb3b', '#ffc107', '#ff9800', '#f57c00', '#e65100', '#bf360c']

def load_geojson():
    """Load Czechia regions GeoJSON if available"""
    # Check these paths in order (add more paths if needed)
    geojson_paths = [
        'data/czechia_regions.geojson',
        'czechia_regions.geojson',
        'data/cze_adm1.geojson'
    ]
    
    for path in geojson_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading GeoJSON from {path}: {e}")
    
    return None  # Returns None if no GeoJSON found (fallback to markers)

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

def create_map(df, selected_region=None, show_individual=False):
    """
    Create interactive map visualization
    Args:
        df: DataFrame with accident data
        selected_region: Region name for drill-down (None = all regions)
        show_individual: If True, show accident bubbles. If False, show region choropleth.
    Returns:
        Plotly figure object
    """
    # Remove records without valid coordinates
    map_df = df[(df['lat'].notna()) & (df['lon'].notna())].copy()
    
    if len(map_df) == 0:
        # Empty map centered on Czechia
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(
            lat=[49.8175],
            lon=[15.4730],
            mode='markers',
            marker=dict(size=1, opacity=0)
        ))
        fig.update_geos(
            center=dict(lat=49.8175, lon=15.4730),  # Czechia center coordinates
            projection_scale=5.0,  # Zoom level (lower = zoomed out)
            visible=True,
            resolution=50,  # Map resolution (50 = medium detail)
            showcountries=True,
            countrycolor='#34495e',  # Country border color
            showland=True,
            landcolor='#f5f5f5',  # Land color
            showocean=True,
            oceancolor='#e8f4f8',  # Ocean color
            lonaxis_range=[12, 19],  # Longitude bounds (west to east)
            lataxis_range=[48.5, 51.1]  # Latitude bounds (south to north)
        )
        fig.update_layout(
            height=700,
            margin=dict(l=0, r=0, t=0, b=0),
            geo=dict(bgcolor='rgba(0,0,0,0)')
        )
        return fig
    
    # Calculate region-level statistics
    region_stats = map_df.groupby('region').agg({
        'severity': 'count',  # Count accidents per region
        'lat': 'mean',  # Region center latitude
        'lon': 'mean'   # Region center longitude
    }).reset_index()
    region_stats.rename(columns={'severity': 'count'}, inplace=True)
    
    # Calculate severity breakdown per region
    severity_breakdown = map_df.groupby('region').agg({
        'severity': lambda x: {
            'Fatal': (x == 'Fatal').sum(),
            'Serious': (x == 'Serious').sum(),
            'Slight': (x == 'Slight').sum()
        }
    }).reset_index()
    
    region_stats = region_stats.merge(severity_breakdown, on='region', how='left')
    
    # Calculate density score: weighted by severity (Fatal=5, Serious=2, Slight=1)
    # Adjust weights here to change density calculation
    region_stats['density_score'] = (
        region_stats['count'] * 1 +  # Base weight for all accidents
        region_stats['severity'].apply(lambda x: x.get('Serious', 0) if isinstance(x, dict) else 0) * 2 +
        region_stats['severity'].apply(lambda x: x.get('Fatal', 0) if isinstance(x, dict) else 0) * 5
    )
    
    # Normalize density score to 0-1 range for color mapping
    if region_stats['density_score'].max() > 0:
        max_score = region_stats['density_score'].max()
        min_score = region_stats['density_score'].min()
        region_stats['color_norm'] = (region_stats['density_score'] - min_score) / (max_score - min_score) if max_score > min_score else 0
    else:
        region_stats['color_norm'] = 0
    
    # Store raw count for display
    region_stats['total_accidents'] = region_stats['count']
    
    # Create figure
    fig = go.Figure()
    
    if show_individual:
        # Show individual accidents as clustered bubbles
        # Round coordinates for clustering (3 decimals = ~100m precision)
        map_df['lat_rounded'] = map_df['lat'].round(3)
        map_df['lon_rounded'] = map_df['lon'].round(3)
        
        aggregated = map_df.groupby(['lat_rounded', 'lon_rounded', 'region']).agg({
            'severity': 'count',
            'lat': 'first',
            'lon': 'first'
        }).reset_index()
        aggregated.rename(columns={'severity': 'count'}, inplace=True)
        
        # Calculate severity breakdown
        severity_breakdown = map_df.groupby(['lat_rounded', 'lon_rounded']).agg({
            'severity': lambda x: {
                'Fatal': (x == 'Fatal').sum(),
                'Serious': (x == 'Serious').sum(),
                'Slight': (x == 'Slight').sum()
            }
        }).reset_index()
        
        aggregated = aggregated.merge(severity_breakdown, on=['lat_rounded', 'lon_rounded'], how='left')
        
        # Calculate density score
        aggregated['density_score'] = (
            aggregated['count'] * 1 +
            aggregated['severity'].apply(lambda x: x.get('Serious', 0) if isinstance(x, dict) else 0) * 2 +
            aggregated['severity'].apply(lambda x: x.get('Fatal', 0) if isinstance(x, dict) else 0) * 5
        )
        
        # Normalize for color
        if aggregated['density_score'].max() > 0:
            max_score = aggregated['density_score'].max()
            min_score = aggregated['density_score'].min()
            aggregated['color_norm'] = (aggregated['density_score'] - min_score) / (max_score - min_score) if max_score > min_score else 0
        else:
            aggregated['color_norm'] = 0
        
        # Limit points for performance (change 2000 to adjust max points)
        if len(aggregated) > 2000:
            aggregated = aggregated.nlargest(2000, 'density_score')
        
        # Create hover text
        aggregated['hover_text'] = aggregated.apply(
            lambda row: f"<b>{row['region']}</b><br>" +
                       f"Total Accidents: {int(row['count'])}<br>" +
                       f"Fatal: {row['severity'].get('Fatal', 0) if isinstance(row['severity'], dict) else 0}<br>" +
                       f"Serious: {row['severity'].get('Serious', 0) if isinstance(row['severity'], dict) else 0}<br>" +
                       f"Slight: {row['severity'].get('Slight', 0) if isinstance(row['severity'], dict) else 0}",
            axis=1
        )
        
        # Create customdata for clicks
        aggregated['customdata'] = aggregated.apply(
            lambda row: {'region': row['region'], 'count': int(row['count'])},
            axis=1
        )
        
        # Calculate marker sizes: min 10px, max 50px (adjust multipliers to change size range)
        marker_sizes = aggregated['count'].apply(lambda x: min(max(x * 0.8 + 8, 10), 50))
        
        fig.add_trace(go.Scattergeo(
            lat=aggregated['lat'],
            lon=aggregated['lon'],
            mode='markers',
            marker=dict(
                size=marker_sizes,
                color=aggregated['color_norm'],
                colorscale='YlOrRd',  # Yellow-Orange-Red scale (change to other Plotly scales if needed)
                showscale=True,
                colorbar=dict(
                    title=dict(text="Accident<br>Density", font=dict(size=12)),  # Colorbar title
                    len=0.5,  # Colorbar length (0-1)
                    y=0.5,    # Colorbar vertical position (0-1)
                    x=1.02,   # Colorbar horizontal position
                    tickfont=dict(size=10),  # Tick label font size
                    tickvals=[0, 0.25, 0.5, 0.75, 1.0],  # Tick positions
                    ticktext=['Low', '', 'Medium', '', 'High']  # Tick labels
                ),
                opacity=0.85,  # Marker opacity (0-1)
                line=dict(width=2, color='white'),  # Border width and color
                cmin=0,  # Color scale minimum
                cmax=1   # Color scale maximum
            ),
            text=aggregated['hover_text'],
            hoverinfo='text',
            customdata=aggregated['customdata'].tolist(),
            selected=dict(marker=dict(size=55, opacity=1, line=dict(width=3, color='#3498db'))) if selected_region else None
        ))
    else:
        # Show regions as choropleth (if GeoJSON available) or as larger markers
        geojson = load_geojson()
        
        if geojson:
            # Create choropleth map with region boundaries
            # Map dataset regions to GADM regions
            # GADM uses NAME_1 (Czech names) as featureidkey
            
            # Create mapping: GADM NAME_1 -> dataset region -> value
            gadm_to_value = {}
            dataset_to_gadm = {}
            
            # Build reverse mapping from our dataset regions to GADM names
            for _, row in region_stats.iterrows():
                dataset_region = row['region']
                # Find corresponding GADM name
                for feature in geojson.get('features', []):
                    props = feature.get('properties', {})
                    gadm_name = props.get('NAME_1', '')
                    if gadm_name:
                        normalized_dataset = normalize_region_name(gadm_name)
                        if normalized_dataset == dataset_region:
                            dataset_to_gadm[dataset_region] = gadm_name
                            gadm_to_value[gadm_name] = row['color_norm']
                            break
                        # Also try VARNAME_1 (English)
                        varname = props.get('VARNAME_1', '')
                        if varname and normalize_region_name(varname) == dataset_region:
                            dataset_to_gadm[dataset_region] = gadm_name
                            gadm_to_value[gadm_name] = row['color_norm']
                            break
            
            # Create locations and z arrays using GADM NAME_1
            locations = []
            z_values = []
            
            for feature in geojson.get('features', []):
                props = feature.get('properties', {})
                gadm_name = props.get('NAME_1', '')
                if gadm_name and gadm_name in gadm_to_value:
                    locations.append(gadm_name)
                    z_values.append(gadm_to_value[gadm_name])
            
            if locations and len(locations) > 0:
                # Create hover text with English names and statistics
                hover_texts = []
                for loc in locations:
                    english_name = normalize_region_name(loc)
                    # Get statistics for this region
                    region_data = region_stats[region_stats['region'] == english_name]
                    if len(region_data) > 0:
                        row = region_data.iloc[0]
                        hover_text = (
                            f"<b>{english_name}</b><br>" +
                            f"Total Accidents: {int(row['total_accidents'])}<br>" +
                            f"Fatal: {row['severity'].get('Fatal', 0) if isinstance(row['severity'], dict) else 0}<br>" +
                            f"Serious: {row['severity'].get('Serious', 0) if isinstance(row['severity'], dict) else 0}<br>" +
                            f"Slight: {row['severity'].get('Slight', 0) if isinstance(row['severity'], dict) else 0}"
                        )
                    else:
                        hover_text = f"<b>{english_name}</b>"
                    hover_texts.append(hover_text)
                
                # Use Choropleth with GADM NAME_1 as featureidkey (for matching)
                # But display English names in hover
                fig.add_trace(go.Choropleth(
                    geojson=geojson,
                    locations=locations,  # GADM Czech names for matching
                    z=z_values,
                    colorscale='YlOrRd',
                    marker_line_color='#34495e',
                    marker_line_width=2,
                    colorbar=dict(
                        title=dict(text="Accident<br>Density", font=dict(size=12)),
                        len=0.5,
                        y=0.5,
                        x=1.02,
                        tickfont=dict(size=10),
                        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                        ticktext=['Low', '', 'Medium', '', 'High']
                    ),
                    featureidkey="properties.NAME_1",  # GADM uses NAME_1
                    text=hover_texts,  # English names and stats for hover
                    hovertemplate='%{text}<extra></extra>',
                    customdata=[{'region': normalize_region_name(loc), 'gadm_name': loc} for loc in locations]
                ))
                print(f"✓ Choropleth map created with {len(locations)} regions (English names)")
            else:
                # Fallback to markers if no matching regions
                print("⚠ No matching regions found, falling back to markers")
                geojson = None
        
        if not geojson:
            # Fallback: Show region centers as larger markers
            region_stats['hover_text'] = region_stats.apply(
                lambda row: f"<b>{row['region']}</b><br>" +
                           f"Total Accidents: {int(row['total_accidents'])}<br>" +
                           f"Fatal: {row['severity'].get('Fatal', 0) if isinstance(row['severity'], dict) else 0}<br>" +
                           f"Serious: {row['severity'].get('Serious', 0) if isinstance(row['severity'], dict) else 0}<br>" +
                           f"Slight: {row['severity'].get('Slight', 0) if isinstance(row['severity'], dict) else 0}",
                axis=1
            )
            
            region_stats['customdata'] = region_stats.apply(
                lambda row: {'region': row['region'], 'count': int(row['total_accidents'])},
                axis=1
            )
            
            marker_sizes = region_stats['total_accidents'].apply(lambda x: min(max(x * 0.3 + 15, 20), 80))
            
            fig.add_trace(go.Scattergeo(
                lat=region_stats['lat'],
                lon=region_stats['lon'],
                mode='markers',
                marker=dict(
                    size=marker_sizes,
                    color=region_stats['color_norm'],
                    colorscale='YlOrRd',
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Accident<br>Density", font=dict(size=12)),
                        len=0.5, 
                        y=0.5, 
                        x=1.02,
                        tickfont=dict(size=10),
                        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                        ticktext=['Low', '', 'Medium', '', 'High']
                    ),
                    opacity=0.85,
                    line=dict(width=2, color='white'),
                    cmin=0,
                    cmax=1
                ),
                text=region_stats['hover_text'],
                hoverinfo='text',
                customdata=region_stats['customdata'].tolist(),
                selected=dict(marker=dict(size=55, opacity=1, line=dict(width=3, color='#3498db'))) if selected_region else None
            ))
    
    # Update geo layout: center on Czechia
    center_lat = 49.8175  # Center latitude
    center_lon = 15.4730  # Center longitude
    
    # Zoom level: lower = zoomed out, higher = zoomed in
    zoom_scale = 5.0 if not selected_region else 7.0  # Zoom in when region selected
    
    fig.update_geos(
        center=dict(lat=center_lat, lon=center_lon),
        projection_scale=zoom_scale,  # Zoom level
        visible=True,
        resolution=50,  # Map detail level (50 = medium, 110 = high detail)
        showcountries=True,
        countrycolor='#34495e',  # Country border color
        showland=True,
        landcolor='#f5f5f5',  # Land fill color
        showocean=True,
        oceancolor='#e8f4f8',  # Ocean fill color
        showlakes=False,
        showrivers=False,
        coastlinecolor='#34495e',  # Coastline color
        bgcolor='white',
        lonaxis_range=[12, 19],  # Longitude bounds (west to east)
        lataxis_range=[48.5, 51.1],  # Latitude bounds (south to north)
        subunitcolor='#bdc3c7',  # Region boundaries color (change to adjust boundary visibility)
        subunitwidth=1  # Boundary line width
    )
    
    fig.update_layout(
        height=700,  # Map height in pixels (change to adjust map size)
        margin=dict(l=0, r=0, t=0, b=0),  # Margins: left, right, top, bottom
        clickmode='event+select',  # Enable click and select interactions
        geo=dict(bgcolor='rgba(0,0,0,0)'),  # Transparent background
        paper_bgcolor='white',  # Paper background color
        plot_bgcolor='white'  # Plot background color
    )
    
    return fig

def create_road_type_chart(df):
    """Create bar chart showing accident frequency by road type"""
    if 'road_type' not in df.columns or df['road_type'].isna().all() or len(df) == 0:
        return create_empty_chart("Road Type Distribution")
    
    # Get top 10 road types (change 10 to show more/fewer)
    road_type_counts = df['road_type'].value_counts().head(10)
    
    if len(road_type_counts) == 0:
        return create_empty_chart("Road Type Distribution")
    
    # Colorblind-safe categorical colors (change Set3 to other Plotly palettes if needed)
    colors = px.colors.qualitative.Set3[:len(road_type_counts)]
    
    fig = go.Figure(data=[
        go.Bar(
            x=road_type_counts.index,
            y=road_type_counts.values,
            marker=dict(color=colors, line=dict(color='white', width=1.5)),  # Bar colors and border
            text=road_type_counts.values,  # Values shown on bars
            textposition='outside',  # Text position: 'outside', 'inside', or 'auto'
            textfont=dict(size=11),  # Text font size
            hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text='Road Type Bar Chart', font=dict(size=14, color='#2c3e50')),  # Chart title
        xaxis=dict(
            title='', 
            tickangle=-45,  # Label rotation angle (change to adjust label angle)
            showgrid=False,
            tickfont=dict(size=10)  # X-axis label font size
        ),
        yaxis=dict(title='Number of Accidents', showgrid=True, gridcolor='#ecf0f1'),
        height=280,  # Chart height in pixels
        margin=dict(l=50, r=20, t=50, b=100),  # Margins: left, right, top, bottom (increase bottom for rotated labels)
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_collision_chart(df):
    """Create donut chart showing collision type distribution"""
    if 'collision_type' not in df.columns or df['collision_type'].isna().all() or len(df) == 0:
        return create_empty_chart("Collision Type Distribution")
    
    collision_counts = df['collision_type'].value_counts()
    
    if len(collision_counts) == 0:
        return create_empty_chart("Collision Type Distribution")
    
    # Colorblind-safe categorical colors
    colors = px.colors.qualitative.Set2[:len(collision_counts)]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=collision_counts.index,
            values=collision_counts.values,
            hole=0.4,  # Donut hole size (0 = pie, 0.4 = donut, change to adjust)
            marker=dict(colors=colors, line=dict(color='white', width=2)),  # Slice colors and borders
            textinfo='label+percent',  # Show label and percentage on slices
            textfont=dict(size=11),  # Text font size
            hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text='Collision Types Pie Chart', font=dict(size=14, color='#2c3e50')),
        height=280,  # Chart height
        margin=dict(l=20, r=20, t=50, b=20),  # Margins
        showlegend=True,
        legend=dict(orientation='v', yanchor='middle', y=0.5, x=1.15, font=dict(size=10)),  # Legend position and size
        paper_bgcolor='white'
    )
    
    return fig

def create_car_brand_chart(df):
    """Create stacked bar chart showing accidents by car brand and severity"""
    if 'car_brand' not in df.columns or df['car_brand'].isna().all() or len(df) == 0:
        return create_empty_chart("Car Brand Safety")
    
    # Get top 10 brands (change 10 to show more/fewer)
    brand_counts = df['car_brand'].value_counts().head(10)
    
    if len(brand_counts) == 0:
        return create_empty_chart("Car Brand Safety")
    
    # Calculate severity breakdown for top brands
    brand_severity = df[df['car_brand'].isin(brand_counts.index)].groupby(['car_brand', 'severity']).size().unstack(fill_value=0)
    
    # Create stacked bar chart: each bar has Slight, Serious, Fatal segments
    fig = go.Figure()
    
    for severity in ['Slight', 'Serious', 'Fatal']:
        if severity in brand_severity.columns:
            fig.add_trace(go.Bar(
                name=severity,
                x=brand_severity.index,
                y=brand_severity[severity],
                marker=dict(
                    color=SEVERITY_COLORS.get(severity, '#95a5a6'),  # Use severity color scheme
                    line=dict(color='white', width=1)  # Segment border
                ),
                hovertemplate=f'<b>%{{x}}</b><br>{severity}: %{{y:,}}<extra></extra>'
            ))
    
    fig.update_layout(
        title=dict(text='Car Brand Safety Bar Chart', font=dict(size=14, color='#2c3e50')),
        xaxis=dict(title='', tickangle=-30, showgrid=False),  # X-axis label rotation
        yaxis=dict(title='Number of Accidents', showgrid=True, gridcolor='#ecf0f1'),
        barmode='stack',  # Stack bars (change to 'group' for side-by-side)
        height=280,  # Chart height
        margin=dict(l=50, r=20, t=50, b=70),  # Margins
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=10))  # Horizontal legend
    )
    
    return fig

def create_sankey_diagram(df):
    """Create Sankey diagram showing flow from collision type to severity"""
    if 'collision_type' not in df.columns or 'severity' not in df.columns:
        return create_empty_chart("Collision to Severity Flow")
    
    # Remove records with missing collision type or severity
    sankey_df = df[df['collision_type'].notna() & df['severity'].notna()].copy()
    
    if len(sankey_df) == 0:
        return create_empty_chart("Collision to Severity Flow")
    
    # Get unique values for nodes
    collision_types = sankey_df['collision_type'].unique()
    severities = sankey_df['severity'].unique()
    
    # Create node list: collision types first, then severities
    nodes = list(collision_types) + list(severities)
    node_indices = {node: i for i, node in enumerate(nodes)}  # Map node name to index
    
    # Calculate flow counts between collision types and severities
    flows = sankey_df.groupby(['collision_type', 'severity']).size().reset_index(name='count')
    
    # Create arrays for Sankey: source nodes, target nodes, and flow values
    source = [node_indices[ct] for ct in flows['collision_type']]  # Source node indices
    target = [node_indices[st] for st in flows['severity']]  # Target node indices
    value = flows['count'].tolist()  # Flow values (accident counts)
    
    # Assign colors to nodes: blue for collision types, severity colors for outcomes
    node_colors = []
    for node in nodes:
        if node in collision_types:
            node_colors.append('#3498db')  # Blue for collision types (change color if needed)
        else:
            node_colors.append(SEVERITY_COLORS.get(node, '#95a5a6'))
    
    # Convert hex colors to rgba for link transparency
    def hex_to_rgba(hex_color, alpha=0.5):
        """Convert hex color to rgba string (alpha = transparency, 0-1)"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        return f"rgba(149, 165, 166, {alpha})"
    
    # Color links based on target severity
    link_colors = []
    for severity in flows['severity']:
        color = SEVERITY_COLORS.get(severity, '#95a5a6')
        link_colors.append(hex_to_rgba(color, alpha=0.5))  # Change alpha to adjust link opacity
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,  # Node padding (spacing between nodes)
            thickness=20,  # Node thickness (change to adjust node width)
            line=dict(color="black", width=0.5),  # Node border
            label=nodes,  # Node labels
            color=node_colors  # Node fill colors
        ),
        link=dict(
            source=source,  # Source node indices
            target=target,  # Target node indices
            value=value,  # Flow values (determines link width)
            color=link_colors,  # Link colors
            hovertemplate='%{source.label} → %{target.label}<br>Count: %{value:,}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(text='Sankey: Collision Type → Severity', font=dict(size=14, color='#2c3e50')),
        height=280,  # Chart height
        margin=dict(l=20, r=20, t=50, b=20),  # Margins
        font_size=10,  # Default font size for labels
        paper_bgcolor='white'
    )
    
    return fig

def create_empty_chart(title):
    """Create an empty chart placeholder"""
    fig = go.Figure()
    fig.add_annotation(
        text="No data available",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color='gray')
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#2c3e50')),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=280
    )
    return fig
