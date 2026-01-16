import dash_mantine_components as dmc
from dash import dcc, html

def filter_dropdown(id:str,label:str,data):
  return html.Div(
    className="col-span-12 sm:col-span-6 md:col-span-4 lg:col-span-12 p-0 m-0 mb-4",
    children=[
      dmc.Select(
        id=id,
        label=label,
        data=['all'] + data,
        value='all',
        persistence=True,
        persistence_type='local',
        allowDeselect=False,
      )
    ]
  )




