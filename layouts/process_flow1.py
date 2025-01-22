from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash_ag_grid as dag
from dash import Dash
#from utils import create_elements  # Import the helper function

# Load and register the dagre layout
cyto.load_extra_layouts()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initial sample data
initial_nodes = [
    {"name": "Raw Materials", "type": "type1"},
    {"name": "Processing Unit", "type": "type2"},
    {"name": "Quality Control", "type": "type3"}
]

initial_edges = [
    {"upstream": "Raw Materials", "downstream": "Processing Unit"},
    {"upstream": "Processing Unit", "downstream": "Quality Control"}
]

def create_elements(nodes, edges):
    """
    Helper function to create Cytoscape elements from nodes and edges.
    """
    elements = [{"data": {"id": node["name"], "label": node["name"]}} for node in nodes]
    elements += [
        {"data": {"source": edge["upstream"], "target": edge["downstream"]}}
        for edge in edges
    ]
    return elements

process_flow_layout = html.Div([
    html.H2("Process Flow Visualization", className="mb-4"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Nodes"),
                dbc.CardBody([
                    dbc.Button("Add Node", id="add-node-btn", color="primary", className="mb-3"),
                    dbc.Button("Delete Selected Node", id="delete-node-btn", color="danger", className="mb-3"),
                    dag.AgGrid(
                        id='node-table',
                        columnDefs=[
                            {"field": "name", "headerName": "Name", "editable": True},
                            {
                                "field": "type",
                                "headerName": "Type",
                                "editable": True,
                                "cellEditor": "agSelectCellEditor",
                                "cellEditorParams": {
                                    "values": ["type1", "type2", "type3"]
                                }
                            }
                        ],
                        rowData=initial_nodes,
                        defaultColDef={"resizable": True},
                        columnSize="sizeToFit"
                    )
                ])
            ], className="mb-3"),

            dbc.Card([
                dbc.CardHeader("Edges"),
                dbc.CardBody([
                    dbc.Button("Add Edge", id="add-edge-btn", color="primary", className="mb-3"),
                    dbc.Button("Delete Selected Edge", id="delete-edge-btn", color="danger", className="mb-3"),
                    dag.AgGrid(
                        id='edge-table',
                        columnDefs=[
                            {"field": "upstream", "headerName": "Upstream Node", "editable": True},
                            {"field": "downstream", "headerName": "Downstream Node", "editable": True}
                        ],
                        rowData=initial_edges,
                        defaultColDef={"resizable": True},
                        columnSize="sizeToFit"
                    )
                ])
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Process Flow Canvas"),
                dbc.CardBody([
                    cyto.Cytoscape(
                        id='process-flow-canvas',
                        layout={'name': 'dagre'},
                        style={'width': '100%', 'height': '600px'},
                        elements=create_elements(initial_nodes, initial_edges)  # Use the helper function here
                    )
                ])
            ])
        ], width=6)
    ]),

    dcc.Store(id='nodes-store', data=initial_nodes),
    dcc.Store(id='edges-store', data=initial_edges)
])

# Callback to add a new node
@app.callback(
    Output('nodes-store', 'data'),
    Input('add-node-btn', 'n_clicks'),
    State('nodes-store', 'data'),
    prevent_initial_call=True
)
def add_node(n_clicks, nodes):
    new_node = {"name": f"Node {len(nodes) + 1}", "type": "type1"}
    nodes.append(new_node)
    return nodes

# Callback to delete a node
@app.callback(
    Output('nodes-store', 'data'),
    Input('delete-node-btn', 'n_clicks'),
    State('node-table', 'selectedRows'),
    State('nodes-store', 'data'),
    prevent_initial_call=True
)
def delete_node(n_clicks, selected_rows, nodes):
    if selected_rows:
        nodes = [node for node in nodes if node not in selected_rows]
    return nodes

# Callback to add a new edge
@app.callback(
    Output('edges-store', 'data'),
    Input('add-edge-btn', 'n_clicks'),
    State('edges-store', 'data'),
    State('nodes-store', 'data'),
    prevent_initial_call=True
)
def add_edge(n_clicks, edges, nodes):
    if len(nodes) >= 2:
        edges.append({"upstream": nodes[0]["name"], "downstream": nodes[1]["name"]})
    return edges

# Callback to delete an edge
@app.callback(
    Output('edges-store', 'data'),
    Input('delete-edge-btn', 'n_clicks'),
    State('edge-table', 'selectedRows'),
    State('edges-store', 'data'),
    prevent_initial_call=True
)
def delete_edge(n_clicks, selected_rows, edges):
    if selected_rows:
        edges = [edge for edge in edges if edge not in selected_rows]
    return edges

# Callback to update canvas
@app.callback(
    Output('process-flow-canvas', 'elements'),
    Input('nodes-store', 'data'),
    Input('edges-store', 'data')
)
def update_canvas(nodes, edges):
    return create_elements(nodes, edges)

# Callback to synchronize node table
@app.callback(
    Output('node-table', 'rowData'),
    Input('nodes-store', 'data')
)
def sync_node_table(nodes):
    return nodes

# Callback to synchronize edge table
@app.callback(
    Output('edge-table', 'rowData'),
    Input('edges-store', 'data')
)
def sync_edge_table(edges):
    return edges

if __name__ == "__main__":
    app.run_server(debug=True)
