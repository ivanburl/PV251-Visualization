from dash import html,dcc

def chart_template(id:str):
  return html.Div(
    className="col-span-12 sm:col-span-6 lg:col-span-12",
    children=[
      dcc.Graph(
        id=id,
        className="h-[220px] border-radius-[8px] bg-white",
      )
    ]
  )