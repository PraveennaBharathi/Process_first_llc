import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from layouts.table_component import table_layout
from layouts.process_flow import process_flow_layout
from layouts.report_generation import report_generation_layout
from layouts.analytics import analytics_layout

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Create the tab content components
tab_process_flow = html.Div(process_flow_layout)
tab_table = html.Div(table_layout)
tab_report = html.Div(report_generation_layout)
tab_analytics = html.Div(analytics_layout)

app.layout = html.Div([
    dbc.NavbarSimple(
        brand="Process First LLC",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dbc.Container([
        html.H1("Process Flow Analytics Dashboard", className="my-4"),
        html.Div([
            dcc.Tabs(
                id='tabs',
                value='tab-process-flow',
                children=[
                    dcc.Tab(
                        label='Process Flow',
                        value='tab-process-flow'
                    ),
                    dcc.Tab(
                        label='Chemical Components',
                        value='tab-table'
                    ),
                    dcc.Tab(
                        label='Report Generation',
                        value='tab-report'
                    ),
                    dcc.Tab(
                        label='Analytics',
                        value='tab-analytics'
                    ),
                ],
                className="mb-4"
            ),
            html.Div(id='tab-content')
        ])
    ], fluid=True)
])

@callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-process-flow':
        return tab_process_flow
    elif tab == 'tab-table':
        return tab_table
    elif tab == 'tab-report':
        return tab_report
    elif tab == 'tab-analytics':
        return tab_analytics
    return tab_process_flow  # Default tab

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
