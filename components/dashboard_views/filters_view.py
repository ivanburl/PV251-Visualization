from dash import html, dcc, Output, Input, clientside_callback, callback
import dash_mantine_components as dmc
from components.filter_dropwdown import filter_dropdown
from components.ids import FILTER_REGION, FILTER_WEATHER, FILTER_ROAD_TYPE, FILTER_ACCIDENT_TYPE, FILTER_VEHICLE_TYPE, \
  FILTER_DATE, FILTER_AGE, FILTER_SHOW_INDIVIDUAL, FILTER_RESET


def render_content(is_mobile,df, regions, weather_conditions,road_types, accident_types, vehicle_types):
  min_age = int(df['age'].min()) if 'age' in df.columns and df['age'].notna().any() else 18
  max_age = int(df['age'].max()) if 'age' in df.columns and df['age'].notna().any() else 80
  content = [
    html.H3(
      className="hidden lg:block col-span-12 mb-4 text-[#34495e] text-xl border-b-2 border-[#bdc3c7] pb-3 font-bold flex-0",
      children="Filters",
    ),
    dmc.Checkbox(
      id=FILTER_SHOW_INDIVIDUAL,
      className="col-span-12 mb-4",
      label="Show Individual Accidents",
      checked=False,
    ),

    html.Hr(
      className='mb-2 border border-[#bdc3c7] col-span-12',
    ),

    filter_dropdown(FILTER_REGION, "Region:", regions),

    html.Div(
      className='col-span-12 sm:col-span-6 md:col-span-4 lg:col-span-12',
      children=[
        # Range date picker
        dmc.DatePickerInput(
          id=FILTER_DATE,
          type='range',
          label='Date Range:',
          valueFormat="YYYY-MM-DD",
          value=[
            df['date'].min() if 'date' in df.columns and df['date'].notna().any() else None,
            df['date'].max() if 'date' in df.columns and df['date'].notna().any() else None,
          ],

        ),
      ]
    ),
    filter_dropdown(FILTER_WEATHER, "Weather:", weather_conditions),
    filter_dropdown(FILTER_ROAD_TYPE, "Road Type:", road_types),
    filter_dropdown(FILTER_ACCIDENT_TYPE, "Accident Type:", accident_types),
    filter_dropdown(FILTER_VEHICLE_TYPE, "Vehicle Type:", vehicle_types),

    html.Div(
      className='col-span-12 mt-4',
      children=[
        html.Label(
          className="font-bold block text-[#2c3e50]",
          children="Age Range:"
        ),
        html.Div(
          className='mb-4',
          children=[
            dmc.RangeSlider(
              id=FILTER_AGE,
              domain=[min_age,max_age],
              value=[10,100],
              marks=[
                {"value":i, "label":str(i)} for i in range(min_age,max_age,10)
              ],
              mb=35
            )
          ],
        ),
      ],
    ),

    dmc.Button(
      id=FILTER_RESET,
      variant="filled",
      className="col-span-12 w-full bg-[#e74c3c] hover:bg-[#c0392b] text-white font-bold",
      children='Reset Filters',
      n_clicks=0,
    ),
  ]

  if is_mobile:
    return dmc.Accordion(
        className="lg:hidden col-span-12 ",
        variant="contained",
        children=[
          dmc.AccordionItem(
            className="text-[#2c3e50]",
            children=[
              dmc.AccordionControl(
                className="text-[#34495e] text-xl font-bold",
                children="Filters"
              ),
              dmc.AccordionPanel(

                children=content,
              )
            ],
            value="filters"
          )
        ],
      )

  return html.Div(
    className="hidden lg:inline col-span-12 mb-4 p-5",
    children=content,
  )


def render_filters_view(df, regions, weather_conditions,road_types, accident_types, vehicle_types):
  return html.Div(
    className='col-span-2 lg:h-full m-0 bg-[#ecf0f1] lg:overflow-y-auto sticky top-0 z-10 grid grid-cols-12 auto-rows-min gap-x-4 ',
    children=[
      dcc.Store(id='screen-size'),
      # Use a one-time interval to attach the resize listener
      dcc.Interval(id='init-resize-listener', max_intervals=1, interval=500),
      # Hidden button to trigger callback on resize
      html.Button(id='resize-trigger', style={'display': 'none'}),
      
      html.Div(
        id='filters-view',
        className="contents",
        children=[
          render_content(True,df, regions, weather_conditions,road_types, accident_types, vehicle_types),
        ]
      )
    ],
  )

# Callback to attach event listener
clientside_callback(
    """
    function(n) {
        if (!n) return window.dash_clientside.no_update;
        
        const triggerResize = () => {
            const btn = document.getElementById('resize-trigger');
            if (btn) btn.click();
        };

        // Attach listener
        window.addEventListener('resize', triggerResize);
        
        // Initial trigger
        setTimeout(triggerResize, 100);
        
        return true;
    }
    """,
    Output('init-resize-listener', 'disabled'),
    Input('init-resize-listener', 'n_intervals')
)

# Callback to update screen size data
clientside_callback(
    """
    function(n) {
        const w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        const b = { sm: 640, md: 768, lg: 1024, xl: 1280, "2xl": 1536 };
        let bp = 'xs';
        if (w >= b["2xl"]) bp = '2xl';
        else if (w >= b["xl"]) bp = 'xl';
        else if (w >= b["lg"]) bp = 'lg';
        else if (w >= b["md"]) bp = 'md';
        else if (w >= b["sm"]) bp = 'sm';
        
        const is_mobile = w < b["lg"];
        const new_data = { width: w, breakpoint: bp, is_mobile: is_mobile };
        
        if (window.prev_screen_size && window.prev_screen_size.is_mobile === is_mobile) {
            return window.dash_clientside.no_update;
        }
        window.prev_screen_size = new_data;
        return new_data;
    }
    """,
    Output('screen-size', 'data'),
    Input('resize-trigger', 'n_clicks'),
)
