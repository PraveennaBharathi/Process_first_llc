from dash import html, dcc, Input, Output, State, callback_context, ALL, callback, exceptions
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash_ag_grid as dag
import string

# Load and register the dagre layout
cyto.load_extra_layouts()

# Initial data
initial_nodes = [
    {"data": {"id": "A", "name": "Node A", "type": "type1"}},
    {"data": {"id": "B", "name": "Node B", "type": "type2"}},
]

initial_edges = [
    {"data": {"id": "AB", "source": "A", "target": "B"}},
]

def get_next_id(existing_nodes):
    """Generate next available alphabetic ID"""
    existing_ids = {node["data"]["id"] for node in existing_nodes}
    for c in string.ascii_uppercase:
        if c not in existing_ids:
            return c
    # If we run out of single letters, start using double letters
    for c1 in string.ascii_uppercase:
        for c2 in string.ascii_uppercase:
            id_str = c1 + c2
            if id_str not in existing_ids:
                return id_str
    return None

def get_edge_columns(nodes):
    return [
        {"field": "id", "headerName": "ID", "hide": True},
        {
            "field": "source",
            "headerName": "Upstream Node",
            "editable": True,
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {"values": [node["data"]["id"] for node in nodes]}
        },
        {
            "field": "target",
            "headerName": "Downstream Node",
            "editable": True,
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {"values": [node["data"]["id"] for node in nodes]}
        }
    ]

def create_edge_id(source, target):
    return f"{source}-{target}"

process_flow_layout = html.Div([
    html.H2("Process Flow Visualization", className="mb-4"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Nodes"),
                dbc.CardBody([
                    dag.AgGrid(
                        id='node-table',
                        columnDefs=[
                            {"field": "id", "headerName": "ID", "editable": True},
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
                        rowData=[{
                            "id": node["data"]["id"], 
                            "name": node["data"]["name"],
                            "type": node["data"]["type"]
                        } for node in initial_nodes],
                        columnSize="sizeToFit",
                        defaultColDef={
                            "resizable": True
                        },
                        dashGridOptions={
                            "rowSelection": "multiple",
                            "enableCellTextSelection": True,
                            "ensureDomOrder": True
                        }
                    )
                ])
            ], className="mb-3"),
            
            dbc.Card([
                dbc.CardHeader("Edges"),
                dbc.CardBody([
                    dag.AgGrid(
                        id='edge-table',
                        columnDefs=get_edge_columns(initial_nodes),
                        rowData=[{
                            "id": edge["data"]["id"],
                            "source": edge["data"]["source"],
                            "target": edge["data"]["target"]
                        } for edge in initial_edges],
                        columnSize="sizeToFit",
                        defaultColDef={
                            "resizable": True
                        },
                        dashGridOptions={
                            "rowSelection": "multiple",
                            "enableCellTextSelection": True,
                            "ensureDomOrder": True
                        }
                    )
                ])
            ]),
            html.Div([
                dbc.Button("Add Node", id="add-node-btn", color="primary", className="me-2"),
                dbc.Button("Add Edge", id="add-edge-btn", color="success", className="me-2"),
                dbc.Button("Delete Selected", id="delete-selected-btn", color="danger")
            ], className="mt-3")
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Process Flow Canvas"),
                dbc.CardBody([
                    cyto.Cytoscape(
                        id='process-flow-canvas',
                        layout={'name': 'dagre', 'rankDir': 'LR'},
                        style={'width': '100%', 'height': '600px'},
                        elements=initial_nodes + initial_edges,
                        stylesheet=[
                            {
                                'selector': 'node',
                                'style': {
                                    'content': 'data(name)',
                                    'text-valign': 'center',
                                    'text-halign': 'center',
                                    'background-color': '#6c757d',
                                    'shape': 'rectangle',
                                    'width': '120px',
                                    'height': '40px'
                                }
                            },
                            {
                                'selector': 'edge',
                                'style': {
                                    'curve-style': 'bezier',
                                    'target-arrow-shape': 'triangle',
                                    'line-color': '#495057',
                                    'target-arrow-color': '#495057',
                                    'width': 2
                                }
                            }
                        ]
                    )
                ])
            ])
        ], width=6)
    ]),
    dcc.Store(id='nodes-store', data=initial_nodes),
    dcc.Store(id='edges-store', data=initial_edges)
])

# Combined callback for node and edge updates
@callback(
    [Output('node-table', 'rowData'),
     Output('edge-table', 'rowData'),
     Output('process-flow-canvas', 'elements')],
    [Input('add-node-btn', 'n_clicks'),
     Input('add-edge-btn', 'n_clicks'),
     Input('node-table', 'cellValueChanged'),
     Input('edge-table', 'cellValueChanged')],
    [State('node-table', 'rowData'),
     State('edge-table', 'rowData'),
     State('nodes-store', 'data'),
     State('edges-store', 'data')]
)
def update_graph(add_node_clicks, add_edge_clicks, node_cell_changed, edge_cell_changed,
                current_nodes, current_edges, nodes_data, edges_data):
    ctx = callback_context
    if not ctx.triggered:
        return current_nodes, current_edges, nodes_data + edges_data
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'add-node-btn':
        next_id = get_next_id([{"data": {"id": row["id"]}} for row in current_nodes])
        if next_id:
            new_node = {"id": next_id, "name": f"Node {next_id}", "type": "type1"}
            current_nodes.append(new_node)
            nodes_data.append({"data": {"id": next_id, "name": f"Node {next_id}", "type": "type1"}})
    
    elif trigger_id == 'add-edge-btn':
        if len(current_nodes) >= 2:
            source = current_nodes[0]["id"]
            target = current_nodes[1]["id"]
            edge_id = create_edge_id(source, target)
            new_edge = {"id": edge_id, "source": source, "target": target}
            current_edges.append(new_edge)
            edges_data.append({"data": {"id": edge_id, "source": source, "target": target}})
    
    elif trigger_id == 'node-table' and node_cell_changed:
        changed_id = node_cell_changed["id"]
        changed_field = node_cell_changed["field"]
        new_value = node_cell_changed["value"]
        
        for node in nodes_data:
            if node["data"]["id"] == changed_id:
                node["data"][changed_field] = new_value
                break
        
        for node in current_nodes:
            if node["id"] == changed_id:
                node[changed_field] = new_value
                break
    
    elif trigger_id == 'edge-table' and edge_cell_changed:
        changed_id = edge_cell_changed["id"]
        changed_field = edge_cell_changed["field"]
        new_value = edge_cell_changed["value"]
        
        for edge in edges_data:
            if edge["data"]["id"] == changed_id:
                edge["data"][changed_field] = new_value
                break
        
        for edge in current_edges:
            if edge["id"] == changed_id:
                edge[changed_field] = new_value
                break
    
    return current_nodes, current_edges, nodes_data + edges_data
