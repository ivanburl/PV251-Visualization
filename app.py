"""
Czechia Road Safety Dashboard
Main Dash application for interactive road accident analysis
"""
import json
import os

import dash
import dash_mantine_components as dmc
from dash import Dash, html


# First load geojson data for regions



external_scripts = [{'src': 'https://cdn.tailwindcss.com'}]

# Initialize Dash app
app = Dash(__name__,use_pages=True,external_scripts=external_scripts)
app.title = "Czechia Road Safety Dashboard"
# Browser tab title

app.layout = dmc.MantineProvider(
    html.Div(
        className="font-sans h-screen w-screen flex flex-col overflow-hidden",
        children=[
            dash.page_container
        ],
    )
)



# Expose server for gunicorn
server = app.server

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
