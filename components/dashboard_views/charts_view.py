from dash import html
import dash_vega_components as dvc
from components.chart_template import chart_template
from components.ids import ROAD_TYPE_CHART, COLLISION_CHART, CAR_BRAND_CHART, SANKEY_CHART


def render_charts_view():
    return html.Div(
      className="col-span-12 lg:col-span-4 p-5 lg:overflow-y-auto box-border sm:gap-8 grid grid-cols-12 lg:flex-0 lg:flex-col",
      children=[
        html.H4(
          className="mb-2 text-[#2c3e50] text-xl font-bold border-b-2  border-color-[#bdc3c7] pb-3 col-span-12",
          children="Analytics Panel",
        ),
        dvc.Vega(
          id=ROAD_TYPE_CHART,
          className="col-span-12 sm:col-span-6 lg:col-span-12",
          opt={"renderer": "svg", "actions": False},
        ),
        dvc.Vega(
          id=COLLISION_CHART,
          className="col-span-12 sm:col-span-6 lg:col-span-12",
          opt={"renderer": "svg", "actions": False},
        ),
        dvc.Vega(
          id=CAR_BRAND_CHART,
          className="col-span-12 sm:col-span-6 lg:col-span-12",
          opt={"renderer": "svg", "actions": False},
        ),

        chart_template(SANKEY_CHART)
      ]
    )