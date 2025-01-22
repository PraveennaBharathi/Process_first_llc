# Process First LLC - Process Flow Analytics Dashboard

This application provides a comprehensive dashboard for visualizing and analyzing process flows in the chemical industry.

## Features

1. **Reusable Table Component**
   - All-in-One paginated table using Dash AG Grid
   - Table and pagination sub-components

2. **Process Flow Visualization**
   - Node and Edge management tables
   - Interactive canvas for process flow visualization
   - Real-time updates between tables and canvas

3. **Report Generation**
   - LLM-powered PDF report generation
   - Integration with experiment results
   - Automated text, tables, and plot generation
   - **Note**: Please wait approximately 30 seconds for the report to be downloaded after clicking the generate button

4. **Analytics Dashboard**
   - Interactive pie chart showing variable impact distribution
   - Dynamic line chart displaying KPI trends across scenarios
   - Real-time data visualization of experiment results

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Cohere API key:
```
COHERE_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

## Project Structure

- `/assets` - Static files (CSS, images)
- `/components` - Reusable Dash components
- `/layouts` - Page layouts for each task
- `/utils` - Utility functions
- `/extra` - Additional development and backup files (stored outside main directory)
- `app.py` - Main application file
- `config.py` - Configuration settings

