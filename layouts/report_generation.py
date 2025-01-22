import io
import json
import traceback
import cohere
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv
import os
import dash
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import re
from datetime import datetime
import base64

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

if not COHERE_API_KEY:
    print("Warning: No Cohere API key found in .env file")

def get_ai_insights(data):
    try:
        co = cohere.Client(COHERE_API_KEY)
        
        # Create a detailed prompt
        prompt = f"""
Analyze this industrial process data and provide a structured, comprehensive technical report in a clean and uniform format.

**Key Requirements:**
- Use consistent indentation and bullet points throughout
- Use bold text sparingly and only for main section headers
- Maintain consistent formatting across all sections
- Focus on actionable insights and clear data presentation

**Input Data:**
• Process Variables: {json.dumps(data.get('top_variables', {}), indent=2)}
• Impact Analysis: {json.dumps(data.get('top_impact', {}), indent=2)}
• Setpoint Analysis: {json.dumps(data.get('setpoint_impact_summary', {}), indent=2)}

**Required Format:**

1. KEY VARIABLE ANALYSIS
   • Temperature (Impact: X%)
      - Current Value: [value] [unit]
      - Confidence Level: [percentage]
      - Critical Range: [range]
      - Impact Level: [level]

   • Pressure (Impact: X%)
      - Current Value: [value] [unit]
      - Confidence Level: [percentage]
      - Critical Range: [range]
      - Impact Level: [level]

   • Flow Rate (Impact: X%)
      - Current Value: [value] [unit]
      - Confidence Level: [percentage]
      - Critical Range: [range]
      - Impact Level: [level]

2. OPTIMIZATION PRIORITIES
   • Primary Targets
      - [Target 1]
      - [Target 2]
      - [Target 3]

   • Expected Improvements
      - Efficiency: [X]% improvement
      - Quality: [specific improvements]
      - Cost: [estimated savings]

3. TECHNICAL RECOMMENDATIONS
   • Immediate Actions
      - [Action 1]
      - [Action 2]
      - [Action 3]

   • Long-term Strategy
      - [Strategy 1]
      - [Strategy 2]
      - [Strategy 3]

4. RISK ASSESSMENT
   • Critical Thresholds
      - Temperature: [range]
      - Pressure: [range]
      - Flow Rate: [range]

   • Safety Protocols
      - [Protocol 1]
      - [Protocol 2]
      - [Protocol 3]

Use consistent bullet points and maintain proper indentation. Replace placeholders with specific numerical values and technical details."""

        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=800,
            temperature=0.7,
            num_generations=1
        )

        # Get the response text
        insights = response.generations[0].text

        # Clean up the response - remove any ### or ** markers
        insights = re.sub(r'#{1,3}\s*', '', insights)  # Remove hashtags
        insights = re.sub(r'\*\*', '', insights)  # Remove asterisks

        return insights

    except Exception as e:
        print(f"AI Error: {str(e)}")
        print(traceback.format_exc())
        return ""

def create_pdf_report(data, include_ai=True):
    try:
        # Create PDF buffer and canvas
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Function to check if we need a new page
        def check_page_break(y_pos, needed_space=100):
            if y_pos < needed_space:
                pdf.showPage()  # Start new page
                pdf.setFont("Helvetica-Bold", 12)  # Reset font after new page
                return height - 50  # Reset y position
            return y_pos

        y = height - 50  # Start 50 points from top
        
        # Add title
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, y, "Process Optimization Report")
        y -= 40
        
        # Try to add AI insights if requested
        if include_ai and COHERE_API_KEY:
            try:
                # Get AI insights
                insights = get_ai_insights(data)
                
                # Add insights to PDF
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(72, y, "Technical Analysis:")
                y -= 25
                
                # Format bullet points with proper indentation
                pdf.setFont("Helvetica", 10)
                current_font = "Helvetica"
                current_size = 10
                
                for line in insights.split('\n'):
                    # Check if we need a new page
                    y = check_page_break(y)
                    if y == height - 50:  # If we started a new page
                        pdf.setFont(current_font, current_size)  # Restore font settings
                    
                    # Skip empty lines
                    if not line.strip():
                        y -= 10
                        continue
                    
                    # Set fonts based on line content
                    if re.match(r'^\d+\.\s+[A-Z\s]+$', line.strip()):  # Main section headers
                        current_font = "Helvetica-Bold"
                        current_size = 12
                        pdf.setFont(current_font, current_size)
                    else:
                        current_font = "Helvetica"
                        current_size = 10
                        pdf.setFont(current_font, current_size)
                    
                    # Calculate indentation level
                    indent = len(line) - len(line.lstrip())
                    indent_points = indent // 2 * 20  # 20 points per indentation level
                    
                    # Draw the line with proper indentation
                    text = line.strip()
                    if text:  # Only draw non-empty lines
                        # Split long lines
                        if len(text) > 80:  # If line is too long
                            words = text.split()
                            current_line = ""
                            for word in words:
                                if len(current_line + " " + word) < 80:
                                    current_line += " " + word
                                else:
                                    pdf.drawString(72 + indent_points, y, current_line.strip())
                                    y -= 15
                                    y = check_page_break(y)
                                    if y == height - 50:  # If we started a new page
                                        pdf.setFont(current_font, current_size)  # Restore font
                                    current_line = word
                            if current_line:
                                pdf.drawString(72 + indent_points, y, current_line.strip())
                                y -= 15
                        else:
                            pdf.drawString(72 + indent_points, y, text)
                            y -= 15
                
                y -= 15
                y = check_page_break(y, 150)  # Check before starting variables section
                
            except Exception as e:
                print(f"AI Error: {str(e)}")
                print(traceback.format_exc())
        
        # Add variables section if present
        if data.get('top_variables'):
            y = check_page_break(y)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(72, y, "Key Process Variables:")
            y -= 25
            
            pdf.setFont("Helvetica", 10)
            for var, details in data['top_variables'].items():
                y = check_page_break(y)
                pdf.drawString(72, y, f"{var}: {details['value']} {details['unit']}")
                y -= 20
        
        # Add impacts section if present
        if data.get('top_impact'):
            y -= 20
            y = check_page_break(y)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(72, y, "Variable Impacts on Process:")
            y -= 25
            
            pdf.setFont("Helvetica", 10)
            for var, impact in data['top_impact'].items():
                y = check_page_break(y)
                pdf.drawString(72, y, f"{var}: {impact*100:.1f}% impact")
                y -= 20
        
        # Add simulation results if present
        if data.get('simulated_summary') and data['simulated_summary'].get('simulated_data'):
            y -= 20
            y = check_page_break(y)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(72, y, "Simulation Results:")
            y -= 25
            
            pdf.setFont("Helvetica", 10)
            for scenario in data['simulated_summary']['simulated_data']:
                y = check_page_break(y)
                pdf.drawString(72, y, f"Scenario {scenario['scenario']}: Equipment = {scenario['equipment']}")
                y -= 20
        
        # Add footer to current page
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawString(72, 30, "Generated by Process First LLC - Process Optimization Report")
        
        # Save and get PDF data
        pdf.save()
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(pdf_data).decode('utf-8')
        
    except Exception as e:
        print(f"PDF Error: {str(e)}")
        print(traceback.format_exc())
        raise

def layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Process Optimization Report", className="mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Time Range"),
                                dcc.Dropdown(
                                    id='time-range',
                                    options=[
                                        {'label': 'Last 24 Hours', 'value': '1'},
                                        {'label': 'Last 7 Days', 'value': '7'},
                                        {'label': 'Last 30 Days', 'value': '30'},
                                        {'label': 'Custom Range', 'value': 'custom'}
                                    ],
                                    value='1',
                                    className="mb-3"
                                ),
                                html.Div(id='custom-date-range', style={'display': 'none'}, children=[
                                    dcc.DatePickerRange(
                                        id='date-range',
                                        start_date=datetime.now().date(),
                                        end_date=datetime.now().date(),
                                        className="mb-3"
                                    )
                                ])
                            ], width=4),
                            dbc.Col([
                                html.Label("Equipment"),
                                dcc.Dropdown(
                                    id='equipment',
                                    options=[
                                        {'label': 'All Equipment', 'value': 'all'},
                                        {'label': 'Reactor A', 'value': 'reactor_a'},
                                        {'label': 'Reactor B', 'value': 'reactor_b'},
                                        {'label': 'Distillation Unit', 'value': 'distillation'}
                                    ],
                                    value='all',
                                    className="mb-3"
                                )
                            ], width=4),
                            dbc.Col([
                                html.Label("Report Type"),
                                dcc.Dropdown(
                                    id='report-type',
                                    options=[
                                        {'label': 'Full Analysis', 'value': 'full'},
                                        {'label': 'Quick Summary', 'value': 'summary'},
                                        {'label': 'Technical Details', 'value': 'technical'},
                                        {'label': 'Safety Overview', 'value': 'safety'}
                                    ],
                                    value='full',
                                    className="mb-3"
                                )
                            ], width=4)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Variables to Include"),
                                dcc.Checklist(
                                    id='variables',
                                    options=[
                                        {'label': ' Temperature', 'value': 'temperature'},
                                        {'label': ' Pressure', 'value': 'pressure'},
                                        {'label': ' Flow Rate', 'value': 'flow_rate'}
                                    ],
                                    value=['temperature', 'pressure', 'flow_rate'],
                                    inline=True,
                                    className="mb-3"
                                )
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Generate Report",
                                    id="generate-button",
                                    color="primary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Download PDF",
                                    id="download-button",
                                    color="secondary",
                                    className="me-2"
                                ),
                                dcc.Download(id="download-pdf")
                            ])
                        ])
                    ])
                ], className="mb-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id="report-content")
                    ])
                ])
            ])
        ])
    ], fluid=True)

# Layout
report_generation_layout = layout()

@callback(
    Output('custom-date-range', 'style'),
    Input('time-range', 'value')
)
def toggle_custom_date_range(time_range):
    if time_range == 'custom':
        return {'display': 'block'}
    return {'display': 'none'}

@callback(
    Output("report-content", "children"),
    [Input("generate-button", "n_clicks")],
    [State("time-range", "value"),
     State("equipment", "value"),
     State("report-type", "value"),
     State("variables", "value"),
     State("date-range", "start_date"),
     State("date-range", "end_date")],
    prevent_initial_call=True
)
def update_report_content(n_clicks, time_range, equipment, report_type, variables, start_date, end_date):
    if n_clicks is None:
        raise PreventUpdate
    
    try:
        # Load data
        with open('mock_results.json', 'r') as f:
            data = json.load(f)
        
        # Filter data based on selections
        filtered_data = {
            'top_variables': {},
            'top_impact': {},
            'setpoint_impact_summary': {}
        }
        
        # Only include selected variables
        for var in variables:
            var_title = var.replace('_', ' ').title()
            if var_title in data['top_variables']:
                filtered_data['top_variables'][var_title] = data['top_variables'][var_title]
            if var_title in data['top_impact']:
                filtered_data['top_impact'][var_title] = data['top_impact'][var_title]
            if var_title in data['setpoint_impact_summary']:
                filtered_data['setpoint_impact_summary'][var_title] = data['setpoint_impact_summary'][var_title]
        
        # Filter equipment if needed
        if equipment != 'all' and 'simulated_summary' in data:
            filtered_data['simulated_summary'] = {
                'simulated_data': [
                    scenario for scenario in data['simulated_summary']['simulated_data']
                    if scenario['equipment'].lower() == equipment
                ]
            }
        
        # Generate report preview
        return dbc.Alert([
            html.H4("Report Preview", className="alert-heading"),
            html.Hr(),
            html.P(f"Time Range: {time_range} days" if time_range != 'custom' else f"Custom Range: {start_date} to {end_date}"),
            html.P(f"Equipment: {equipment.replace('_', ' ').title()}"),
            html.P(f"Report Type: {report_type.replace('_', ' ').title()}"),
            html.P(f"Variables: {', '.join(var.replace('_', ' ').title() for var in variables)}")
        ], color="info")
            
    except Exception as e:
        print(f"Error generating preview: {str(e)}")
        print(traceback.format_exc())
        return dbc.Alert(f"Error generating report preview: {str(e)}", color="danger")

@callback(
    Output("download-pdf", "data"),
    [Input("download-button", "n_clicks")],
    [State("time-range", "value"),
     State("equipment", "value"),
     State("report-type", "value"),
     State("variables", "value"),
     State("date-range", "start_date"),
     State("date-range", "end_date")],
    prevent_initial_call=True
)
def download_report(n_clicks, time_range, equipment, report_type, variables, start_date, end_date):
    if n_clicks is None:
        raise PreventUpdate
    
    try:
        # Load data
        with open('mock_results.json', 'r') as f:
            data = json.load(f)
        
        # Filter data based on selections
        filtered_data = {
            'top_variables': {},
            'top_impact': {},
            'setpoint_impact_summary': {}
        }
        
        # Only include selected variables
        for var in variables:
            var_title = var.replace('_', ' ').title()
            if var_title in data['top_variables']:
                filtered_data['top_variables'][var_title] = data['top_variables'][var_title]
            if var_title in data['top_impact']:
                filtered_data['top_impact'][var_title] = data['top_impact'][var_title]
            if var_title in data['setpoint_impact_summary']:
                filtered_data['setpoint_impact_summary'][var_title] = data['setpoint_impact_summary'][var_title]
        
        # Filter equipment if needed
        if equipment != 'all' and 'simulated_summary' in data:
            filtered_data['simulated_summary'] = {
                'simulated_data': [
                    scenario for scenario in data['simulated_summary']['simulated_data']
                    if scenario['equipment'].lower() == equipment
                ]
            }
        
        # Generate PDF
        pdf_base64 = create_pdf_report(filtered_data, include_ai=True)
        return dict(
            content=pdf_base64,
            filename=f'process_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            type='application/pdf',
            base64=True
        )
            
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        print(traceback.format_exc())
        return None
