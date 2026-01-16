# python
# File: components/dashboard_views/map_view.py
import numpy as np
from dash import html, Output, Input, callback, State, dcc, clientside_callback
from components.ids import REGIONAL_DETAILS, SELECTED_REGION_STORAGE, MAP_REGIONAL_LAYER, MAP_CLUSTERING_LAYER, \
  MAP_VIEW_MODE_STORAGE
import dash_leaflet as dl
from dash_extensions.javascript import assign, arrow_function

from utils.utils import load_geojson

MAP_RESIZE_INTERVAL = "map-resize-interval"
MAP_DUMMY_STORE = "map-dummy-store"

clientside_callback(
    """
    function(n) {
      if (!n) return '';
      // petit délai pour laisser le DOM se stabiliser
      setTimeout(function(){ window.dispatchEvent(new Event('resize')); }, 200);
      return '';
    }
    """,
    Output(MAP_DUMMY_STORE, "data"),
    Input(MAP_RESIZE_INTERVAL, "n_intervals")
)


colorscale = ["#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#BD0026", "#800026"]
classes = np.linspace(0, 1, len(colorscale)).tolist()

def render_map_view():


  gradient_css = f"linear-gradient(to right, {', '.join(colorscale)})"

  style_handle = assign("""function(feature, context){
      const {classes, colorscale, style, colorProp} = context.hideout; 
      const value = feature.properties[colorProp];

      // On copie le style de base
      var styleCopy = Object.assign({}, style);

      for (let i = 0; i < classes.length; ++i) {
          if (value > classes[i]) {
              styleCopy.fillColor = colorscale[i];
          }
      }
      return styleCopy;
  }""")

  return html.Div(
    className="col-span-6 w-full flex flex-col relative h-[500px] lg:h-full",
    children=[
        dcc.Store(id=MAP_DUMMY_STORE),
        dcc.Interval(id=MAP_RESIZE_INTERVAL, interval=500, max_intervals=1),

      html.H4(
        className="flex-none absolute z-[1000] mb-4 text-[#34495e] text-xl lg:text-2xl text-center w-full font-bold",
        children="Czechia Map - Accident Hotspots"
      ),
      dl.Map(
        id="leaflet-map",
        className="flex-1 w-full min-h-0",
        center=(49.8175, 15.4730),
        zoom=6,
        children=[
          dl.Pane(name="highlight_pane", style={"zIndex": 650, "pointerEvents": "none"}),
          dl.TileLayer(
            url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
          ),
          # Cluster point layer

          dl.GeoJSON(
            id=MAP_CLUSTERING_LAYER,
            cluster=True,
            superClusterOptions={"radius": 150},
          ),

          # choropleth layer
          dl.GeoJSON(
            id=MAP_REGIONAL_LAYER,
            data=load_geojson(),
            style=style_handle,
            zoomToBounds=False,
            hoverStyle=arrow_function(dict(weight=5, color="#666", dashArray="")),
            hideout={
              "colorscale":colorscale,
              "classes":classes,
              "style":{
                "weight":2,
                "opacity":1,
                "color":"black",
                "fillColor":"white",
                "fillOpacity":1
              },
              "colorProp":
              "density",
              "selected":[]
            },
          ),
          dl.GeoJSON(
            id="geojson-highlight",
            options=dict(interactive=False, pane="highlight_pane"),
            style=dict(color="#000000", weight=4, opacity=1, fillOpacity=0, dashArray="")
          ),
          # color legend
          html.Div(
            className="leaflet-control absolute bottom-4 left-4 z-1000 bg-white p-2 rounded shadow-md w-64",
            children=[
              html.Div(
                className="font-bold mb-2",
                children="Accident Density",
              ),
              html.Div(
                className="w-full h-4",
                style={"background": gradient_css}
              ),
              html.Div(
                className="flex justify-between mt-1 text-sm text-[#555]",
                children=[
                  html.Span("Low"),
                  html.Span("Medium"),
                  html.Span("High")
                ]
              )
            ]
          ),
          # Regional details panel
          html.Div(
            id=REGIONAL_DETAILS,
            className=' z-[1001] md:min-w-64 top-4 right-4 absolute',
          )
        ],
      ),
    ]
  )

@callback(
  [Output(MAP_REGIONAL_LAYER, 'hideout')],
  [Input(MAP_VIEW_MODE_STORAGE, 'data')]
)
def update_map_view_mode_style(view_mode):
  isRegion = (view_mode == 'region')
  if isRegion:
    return {
      "colorscale":colorscale,
      "classes":classes,
      "style":{
        "weight":2,
        "opacity":1,
        "color":"black",
        "fillColor":"white",
        "fillOpacity":1
      },
      "colorProp":
      "density",
      "selected":[]
    },
  else:
    return {
      "colorscale": colorscale,
      "classes": classes,
      "style": {
        "weight": 2,
        "opacity": 1,
        "color": "black",
        "fillColor": "white",
        "fillOpacity": 0
      },
      "colorProp":
        "density",
      "selected": []
    },

@callback(
  [
    Output(SELECTED_REGION_STORAGE, 'data', allow_duplicate=True),
    Output("geojson-highlight","data")
  ],
  [Input(MAP_REGIONAL_LAYER, 'n_clicks')],
  [Input("geojson-highlight", 'n_clicks')],
  [
    State(MAP_VIEW_MODE_STORAGE, 'data'),
    State(MAP_REGIONAL_LAYER, 'clickData'),
    State(SELECTED_REGION_STORAGE, 'data'),
  ],
  prevent_initial_call=True
)
def update_selected_region(_,i,view_mode, click_data, current_selection):
  if not click_data:
    return None, None

  clicked_region = click_data["properties"]['NAME_1']

  if clicked_region == current_selection:
    return None, None

  return clicked_region, click_data
