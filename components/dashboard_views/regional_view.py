from dash import html
def render_regional_view(selected_region, total_accidents, fatalities, serious, slight, avg_age, top_road_type, top_brand):
  fatal_percent = (fatalities / total_accidents) * 100 if total_accidents > 0 else 0
  serious_percent = (serious / total_accidents) * 100 if total_accidents > 0 else 0
  slight_percent = (slight / total_accidents) * 100 if total_accidents > 0 else 0

  return html.Div(
    className="bg-white rounded-lg shadow-md py-2 w-full",
    children=[
      html.Div(
        className="flex flex-row justify-between px-4 py-2 gap-x-2 md:gap-x-4",
        children=[
          html.Div(
            className="text-left flex flex-col  justify-normal",
            children=[
              html.P(
                className="text-gray-500 uppercase tracking-tight text-xs font-medium",
                children="Region",
              ),
              html.P(
                className="text-gray-900 font-bold text-lg md:text-xl",
                children=selected_region,
              ),
            ]
          ),
          html.Div(
            className='text-right flex flex-col',
            children=[
              html.P(
                className="text-gray-500 uppercase tracking-tight font-medium text-xs",
                children="Total ",
              ),
              html.P(
                className="text-gray-900 font-bold text-lg text-xl",
                children=total_accidents,
              )
            ]
          )
        ]
      ),
      html.Div(
        className="mx-4 px-2 rounded-lg border border-gray-200 flex flex-col bg-gray-100 mb-2",
        children=[
          html.P(
            className="text-xs text-gray-500 tracking-tight uppercase font-semibold mt-2 mb-1",
            children="Severity"
          ),
          html.Div(
            className="flex flex-col",
            children=[
              severity_div("Fatal","bg-red-500",fatalities,fatal_percent),
              severity_div("Serious","bg-yellow-800",serious,serious_percent),
              severity_div("Slight","bg-yellow-400",slight,slight_percent),
            ]
          )
        ]
      ),
      html.Div(
        className="mx-4 px-2 rounded-lg border border-gray-200 flex flex-col bg-gray-100 mb-2",
        children=[
          html.P(
            className="text-xs text-gray-500 tracking-tight uppercase font-semibold mt-2 mb-1",
            children="Additional Info"
          ),
          html.Div(
            className="flex flex-col gap-y-2 mb-2",
            children=[
              html.Div(
                className="flex flex-row gap-2 md:gap-4 justify-between",
                children=[
                  html.P(
                    className="text-gray-700 text-xs",
                    children="Average Age",
                  ),
                  html.P(
                    className="text-gray-900 font-bold text-right",
                    children=f"{avg_age:.1f}",
                  )
                ]
              ),
              html.Div(
                className="flex flex-row gap-2 md:gap-4 justify-between",
                children=[
                  html.P(
                    className="text-gray-700 text-xs",
                    children="Top Road Type",
                  ),
                  html.P(
                    className="text-gray-900 font-bold text-right",
                    children=top_road_type,
                  )
                ]
              ),
              html.Div(
                className="flex flex-row gap-2 md:gap-4 justify-between",
                children=[
                  html.P(
                    className="text-gray-700 text-xs",
                    children="Top Car Brand",
                  ),
                  html.P(
                    className="text-gray-900 font-bold text-right",
                    children=top_brand,
                  )
                ]
              ),
            ]
          )
        ],
      )
    ]
  )


def severity_div(label:str,color:str,value:int, value_percent:float):
  return html.Div(
        className="flex flex-col mb-2",
        children=[
          html.Div(
            className="flex flex-row gap-x-2 md:gap-x-4 justify-between",
            children=[
              html.Div(
                className="flex flex-row items-center",
                children=[
                  html.Span(className=f"w-1 h-1 {color} rounded-full inline-block mr-1"),
                  html.P(
                    className="text-gray-700 text-xs",
                    children=label,
                  ),
                ],
              ),
              html.Div(
                className="text-gray-900 flex flex-row gap-1 md:gap-2 items-center font-bold text-right",
                children=[
                  html.P(value),
                  html.Div(
                    className="text-xs text-gray-600 font-light bg-gray-200 rounded-sm px-1",
                    children=f"{value_percent:.2f}%",
                  )
                ],
              )
            ],
          ),
        ]
      )
