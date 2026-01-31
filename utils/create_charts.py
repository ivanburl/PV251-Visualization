import plotly.graph_objects as go
import plotly.express as px
import dash_leaflet.express as dlx

import altair as alt
alt.data_transformers.enable("vegafusion")

import pandas as pd
from pandas import DataFrame

from utils.utils import normalize_region_name, load_geojson

SEVERITY_COLORS = {
    'Slight': '#f1c40f',  # Yellow
    'Serious': '#e67e22',  # Orange
    'Fatal': '#e74c3c'     # Red
}

def get_data_aggregated_by_region(map_df):

  if map_df.empty:
    return pd.DataFrame(columns=['region', 'color_norm', 'density_score'])

  weights = {'Fatal': 6, 'Serious': 3, 'Slight': 1}

  work_df = map_df.copy()
  work_df['accident_score'] = work_df['severity'].map(weights).fillna(1)

  # Calculate region-level statistics
  region_stats = work_df.groupby('region').agg({
    'severity': 'count',
    'accident_score': 'sum',
    'lat': 'mean',
    'lon': 'mean'
  }).reset_index()

  region_stats.rename(columns={
    'severity': 'count',
    'accident_score': 'density_score'
  }, inplace=True)

  max_score = region_stats['density_score'].max()
  min_score = region_stats['density_score'].min()

  if max_score > min_score:
    region_stats['color_norm'] = (region_stats['density_score'] - min_score) / (max_score - min_score)
  elif max_score > 0:
    region_stats['color_norm'] = 1.0
  else:
    region_stats['color_norm'] = 0.0

  return region_stats

def get_geojson_region(df, selected_region=None):
  """
  Add density values to GeoJSON region properties to enable choropleth mapping
  """
  # Load GeoJSON once
  geojson=load_geojson()
  if geojson is None:
    print("Error: GeoJSON data not available.")
    return None

  map_df = df[(df['lat'].notna()) & (df['lon'].notna())].copy()

  if len(map_df) == 0:
    return geojson

  # Get the data aggregated by region
  data_aggregates = get_data_aggregated_by_region(map_df)

  if 'color_norm' not in data_aggregates.columns:
    print("Error: 'color_norm' not found in data aggregates.")
    return geojson

  density_dict = dict(zip(
    data_aggregates['region'],
    data_aggregates['color_norm']
  ))

  # 3. Injection des données
  count_matches = 0  # Pour le debug

  # Add density to GeoJSON properties
  regions_geo = geojson["features"]

  # For each region in GeoJSON, add the density value from data_aggregates
  for feature in geojson["features"]:
    props = feature.get('properties', {})
    gadm_name = props.get('NAME_1', '')  # Vérifiez que c'est bien NAME_1 dans votre JSON

    density_val = 0.0  # Float par défaut

    if gadm_name:
      normalized_name = normalize_region_name(gadm_name)

      # Récupération instantanée via le dictionnaire
      # .get() renvoie 0.0 si la région n'est pas trouvée
      val = density_dict.get(normalized_name, 0.0)

      # FORCE LE TYPE FLOAT (Crucial pour Dash/JSON)
      density_val = float(val)

      if density_val > 0:
        count_matches += 1

    # Injection
    feature['properties']['density'] = density_val

  return geojson

def get_geojson_cluster(df):
  map_df = df[(df['lat'].notna()) & (df['lon'].notna())].copy()

  if len(map_df) == 0:
    return None

  geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c["severity"])} for c in map_df.to_dict('records')])
  # Get all points with severity and coordinates
  return geojson
  # Add any necessary properties for clustering if needed


# Define color scheme for accident severity
def create_road_type_chart(df:DataFrame):
  """Create bar chart showing accident frequency by road type"""
  if 'road_type' not in df.columns or df['road_type'].isna().all() or len(df) == 0:
    return create_empty_chart("Road Type Distribution")

  # Get top 10 road types (change 10 to show more/fewer)
  road_type_counts = df['road_type'].value_counts().head(10).reset_index()
  road_type_counts.columns = ['road_type', 'count']

  if len(road_type_counts) == 0:
    return create_empty_chart("Road Type Distribution")

  # 1. On définit une BASE commune (pour ne pas répéter x et y)
  base = alt.Chart(road_type_counts).encode(
    x=alt.X(
      shorthand='road_type',
      axis=alt.Axis(
        title=None,
        labelAngle=0,
        labelFontSize=10,
        grid=False
      )
    ),
    y=alt.Y(
      shorthand='count',
      axis=alt.Axis(
        title='Number of Accidents',
        grid=True,
        gridColor='#ecf0f1'
      )
    )
  )


  bars = base.mark_bar(
    stroke='white',
    strokeWidth=1.5
  ).encode(
    color=alt.Color('road_type', legend=None),
  )

  text = base.mark_text(
    align='center',
    baseline='middle',
    dy=-10,
    fontSize=11
  ).encode(
    text='count'
  )

  fig = (bars + text).properties(
    width="container",
    height=220,
    title=alt.TitleParams(
      text='Road Type Bar Chart',
      fontSize=14,
      color='#2c3e50',
    )
  ).configure_view(
    stroke=None
  )

  return fig


def create_collision_chart(df):
  """Create donut chart showing collision type distribution"""
  if 'collision_type' not in df.columns or df['collision_type'].isna().all() or len(df) == 0:
    return create_empty_chart("Collision Type Distribution")

  collision_counts = df['collision_type'].value_counts().reset_index()
  collision_counts.columns = ['collision_type', 'count']

  if len(collision_counts) == 0:
    return create_empty_chart("Collision Type Distribution")

  collision_counts = collision_counts.sort_values('collision_type')
  collision_counts['percent'] = collision_counts['count'] / collision_counts['count'].sum()

  # Labels externes
  collision_counts['label_text'] = collision_counts.apply(
    lambda x: [str(x['collision_type']), f"{x['percent']:.0%}"], axis=1
  )
  # Colorblind-safe categorical colors
  chart_colors = px.colors.qualitative.Set2[:len(collision_counts)]

  select = alt.selection_point(
    fields=['collision_type'],
    on='pointerdown',
    clear='dblclick',
    empty=True
  )

  base = alt.Chart(collision_counts)

  pie = base.mark_arc(
    innerRadius=45,
    stroke='white',
    strokeWidth=2
  ).encode(
    theta=alt.Theta(
      shorthand="count",
      stack=True
    ),
    color=alt.Color(
      shorthand="collision_type",
      scale=alt.Scale(range=chart_colors),
      legend=alt.Legend(title="Collision Type", orient='right',titleFontSize=13, labelFontSize=12)
    ),
    opacity=alt.condition(select, alt.value(1), alt.value(0.3)),
    tooltip=[
      alt.Tooltip("collision_type", title="Type"),
      alt.Tooltip("count", title="Count", format=","),
      alt.Tooltip("percent", title="Percentage", format=".1%")
    ]
  ).add_params(select)

  outer_text = base.mark_text(radius=80).encode(
    theta=alt.Theta("count", stack=True),  # Nécessaire pour suivre les parts
    text=alt.Text("label_text"),
    color=alt.value("black"),
    order = alt.Order("collision_type")
  )

  center_info = (base.transform_filter(select)
  .transform_window(
    total_rows='count()',
    frame=[None, None]
  ).transform_calculate(
    central_label="datum.total_rows > 1 ? 'Total' : datum.collision_type"
  ).transform_aggregate(
    total_count='sum(count)',
    groupby=['central_label']
  ))

  text_count = center_info.mark_text(radius=0, fontSize=20, fontWeight='bold', color='#2c3e50').encode(
    text=alt.Text("total_count:Q", format=",")
  )

  # Text labels
  text_label = center_info.mark_text(radius=0, dy=20, fontSize=12, color='gray').encode(
    text=alt.Text("central_label:N")
  )

  fig = (pie + outer_text + text_count + text_label).properties(
    title=alt.TitleParams(text='Collision Types Pie Chart', fontSize=14, color='#2c3e50'),
    width="container",
    height=220
  ).configure_view(
    stroke=None
  )

  return fig


def create_car_brand_chart(df):
  """Create stacked bar chart showing accidents by car brand and severity using Altair"""

  if 'car_brand' not in df.columns or df['car_brand'].isna().all() or len(df) == 0:
    return create_empty_chart("Car Brand Safety")

  top_brands = df['car_brand'].value_counts().head(10).index.tolist()

  if not top_brands:
    return create_empty_chart("Car Brand Safety")

  chart_data = df[df['car_brand'].isin(top_brands)].copy()

  severity_order = ['Fatal', 'Serious', 'Slight']

  available_severities = [s for s in severity_order if s in chart_data['severity'].unique()]

  domain = available_severities
  range_colors = [SEVERITY_COLORS.get(s, '#95a5a6') for s in domain]

  select = alt.selection_point(
    fields=['car_brand'],
    on='pointerdown',
    clear='dblclick',
    empty=True
  )

  base = alt.Chart(chart_data).encode(
    x=alt.X(
      shorthand='car_brand',
      sort='-y',
      axis=alt.Axis(title=None, labelAngle=-30, grid=False)
    )
  )

  bars = base.mark_bar(stroke='white', strokeWidth=1).encode(
    y=alt.Y('count()', axis=alt.Axis(title='Number of Accidents', grid=True, gridColor='#ecf0f1')),

    color=alt.Color(
      shorthand='severity',
      scale=alt.Scale(domain=domain, range=range_colors),
      legend=alt.Legend(title="Severity", orient='top')
    ),

    order=alt.Order('severity', sort='ascending'),

    opacity=alt.condition(select, alt.value(1), alt.value(0.3)),

    tooltip=['car_brand', 'severity', 'count()']
  ).add_params(select)

  text_total = base.mark_text(dy=-10, fontWeight='bold', fontSize=12).encode(
    x=alt.X('car_brand', sort='-y'),
    y=alt.Y('count()'),
    text=alt.Text('count()', format=','),
    color=alt.value('black'),
    opacity=alt.condition(select, alt.value(1), alt.value(0))
  )

  fig = (bars + text_total).properties(
    title=alt.TitleParams(text='Car Brand Safety (Top 10)', fontSize=14, color='#2c3e50'),
    width="container",
    height=220
  ).configure_view(
    stroke=None
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
    height=220,
    margin=dict(l=20, r=20, t=50, b=20),  # Margins
    font_size=10,  # Default font size for labels
    paper_bgcolor='white'
  )

  return fig


def create_empty_chart(title)-> alt.Chart:
  """Create an empty chart placeholder"""

  source = pd.DataFrame(
    {
      'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
      'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
    }
  )

  fig = alt.Chart(source,title=title).mark_bar().encode(
      x='a',
      y='b'
  )
  return fig