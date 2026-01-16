from dash import html

def render_header():
    return html.Div(
      className="bg-[#ecf0f1] shadow-md",
      children=[
        html.H1(
          className="text-center m-0 text-[#2c3e50] text-xl md:text-4xl font-bold pt-5 pb-2 ",
          children="Czechia Road Safety Dashboard",
        ),
        html.P(
          className="text-center text-[#7f8c8d] m-0 md:text-lg text-sm pb-4",
          children="Comprehensive Czechia Road Safety Analysis",
        )
      ]
    )