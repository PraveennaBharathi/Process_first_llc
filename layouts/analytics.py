from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import os

# Load mock results using absolute path
mock_results_path = os.path.join(os.path.dirname(__file__), '..', 'mock_results.json')
with open(mock_results_path, 'r') as f:
    mock_data = json.load(f)

# Create sample visualizations
def create_impact_pie():
    data = mock_data['top_impact']
    fig = px.pie(
        values=list(data.values()),
        names=list(data.keys()),
        title="Variable Impact Distribution"
    )
    return fig

def create_kpi_trend():
    data = mock_data['simulated_summary']['simulated_data']
    df = pd.DataFrame(data)
    fig = px.line(
        df, 
        x='scenario', 
        y='kpi_value',
        title="KPI Trend Across Scenarios"
    )
    return fig

analytics_layout = html.Div([
    html.H2("Analytics Dashboard", className="mb-4"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_impact_pie())
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(figure=create_kpi_trend())
                ])
            ])
        ], width=6)
    ])
])
