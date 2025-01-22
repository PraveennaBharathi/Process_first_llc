import dash_ag_grid as dag
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Read the CSV file from the layouts directory
csv_path = os.path.join(os.path.dirname(__file__), 'chemical_components.csv')
data = pd.read_csv(csv_path).to_dict('records')

# Column definitions based on the CSV structure
columnDefs = [
    {"field": "id", "headerName": "ID", "width": 70},
    {"field": "name", "headerName": "Chemical Name", "width": 150},
    {"field": "formula", "headerName": "Formula", "width": 120},
    {"field": "molecular_weight", "headerName": "Molecular Weight (g/mol)", "width": 180},
    {"field": "hazard", "headerName": "Hazard Classification", "width": 180}
]

# Reusable table component
def create_table(data, columnDefs, paginationPageSize=5):
    return html.Div([
        html.H2("Reusable Table Component", className="mb-4"),
        dbc.Card([
            dbc.CardBody([
                dag.AgGrid(
                    id='data-table',
                    columnDefs=columnDefs,
                    rowData=data,
                    columnSize="sizeToFit",
                    defaultColDef={
                        "resizable": True,
                        "sortable": True,
                        "filter": True
                    },
                    dashGridOptions={
                        "pagination": True,
                        "paginationPageSize": paginationPageSize,
                    }
                )
            ])
        ])
    ])

# Example usage
table_layout = html.Div([
    html.H2("Chemical Components Table", className="mb-4"),
    dbc.Card([
        dbc.CardBody([
            dag.AgGrid(
                id='data-table',
                columnDefs=columnDefs,
                rowData=data,
                columnSize="sizeToFit",
                defaultColDef={
                    "resizable": True,
                    "sortable": True,
                    "filter": True,
                    "floatingFilter": True
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 10,
                }
            )
        ])
    ])
])
