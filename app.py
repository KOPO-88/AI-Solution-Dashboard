import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime
import uuid

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app with external stylesheets
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
        'https://codepen.io/chriddyp/pen/bWLwgP.css'
    ]
)
server = app.server

# Load and clean data
try:
    df = pd.read_csv('al_solutions_sales_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['timestamp', 'continent', 'country', 'product_type', 'request_type', 'salesperson_id'])
    df['revenue ($)'] = pd.to_numeric(df['revenue ($)'], errors='coerce').fillna(0)
    df['purchase_flag'] = pd.to_numeric(df['purchase_flag'], errors='coerce').fillna(0)
    df['job_type'] = df['job_type'].fillna('None')
    df['request_type'] = df['request_type'].fillna('Unknown')
    df['affiliate_code'] = df['affiliate_code'].fillna('None')
    logger.info(f"Loaded {len(df)} rows after cleaning")
except Exception as e:
    logger.error(f"Error loading data: {str(e)}")
    df = pd.DataFrame(columns=['timestamp', 'continent', 'country', 'salesperson_id', 'product_type', 'request_type', 'job_type', 'revenue ($)', 'purchase_flag', 'affiliate_code'])

# Create continent-to-country mapping
continent_countries = df.groupby('continent')['country'].unique().to_dict() if not df.empty else {}
continent_options = [{'label': c, 'value': c} for c in sorted(df['continent'].unique())] if not df.empty else []

# Product filter options
product_options = [{'label': p, 'value': p} for p in sorted(df['product_type'].unique())] if not df.empty else []
logger.info(f"Product options: {product_options}")

# Date range for filter
min_date = df['timestamp'].min().date() if not df.empty else datetime(2024, 1, 1).date()
max_date = df['timestamp'].max().date() if not df.empty else datetime(2025, 5, 31).date()

# Define targets
TARGETS = {
    'revenue': 500000,
    'conversion_rate': 20,
    'demo_to_purchase': 30,
    'jobs_placed': 50,
    'ai_assist_requests': 100,
    'promo_requests': 50
}

# Layout with Heading, Filter Panel, and Summary Statistics Section
app.layout = dbc.Container([
    # Heading
    html.H1("Al-Solutions Team Sales Performance Dashboard", className="text-center mb-3 mt-3", style={'color': '#2c3e50', 'fontWeight': 'bold', 'fontSize': '28px'}),
    
    # Filter Panel
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Dashboard Filters", className="text-center mb-2", style={'color': '#34495e', 'fontWeight': '600', 'fontSize': '16px'}),
                dbc.Row([
                    # Continent
                    dbc.Col([
                        html.Label("Continent", style={'color': '#34495e', 'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='continent-filter',
                            options=continent_options,
                            placeholder="Select Continent",
                            style={
                                'width': '100%', 
                                'fontSize': '12px', 
                                'borderRadius': '4px', 
                                'border': '1px solid #ced4da',
                                'backgroundColor': '#ffffff',
                                'height': '30px'
                            },
                            className="shadow-sm"
                        )
                    ], width=2, className="p-1"),
                    # Countries
                    dbc.Col([
                        html.Label("Countries", style={'color': '#34495e', 'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='country-filter',
                            multi=True,
                            placeholder="Select Countries",
                            style={
                                'width': '100%', 
                                'fontSize': '12px', 
                                'borderRadius': '4px', 
                                'border': '1px solid #ced4da',
                                'backgroundColor': '#ffffff',
                                'height': '30px'
                            },
                            className="shadow-sm"
                        )
                    ], width=2, className="p-1"),
                    # Products
                    dbc.Col([
                        html.Label("Products", style={'color': '#34495e', 'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='product-filter',
                            options=product_options,
                            multi=True,
                            placeholder="Select Products",
                            style={
                                'width': '100%', 
                                'fontSize': '12px', 
                                'borderRadius': '4px', 
                                'border': '1px solid #ced4da',
                                'backgroundColor': '#ffffff',
                                'height': '30px'
                            },
                            className="shadow-sm"
                        )
                    ], width=2, className="p-1"),
                    # Date Range
                    dbc.Col([
                        html.Label("Date Range", style={'color': '#34495e', 'fontSize': '12px'}),
                        dcc.DatePickerRange(
                            id='date-filter',
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            initial_visible_month=max_date,
                            start_date=min_date,
                            end_date=max_date,
                            style={
                                'width': '100%', 
                                'fontSize': '12px', 
                                'borderRadius': '4px', 
                                'border': '1px solid #ced4da',
                                'backgroundColor': '#ffffff'
                            },
                            className="shadow-sm"
                        )
                    ], width=3, className="p-1"),
                    # Trend View
                    dbc.Col([
                        html.Label("Trend View", style={'color': '#34495e', 'fontSize': '12px'}),
                        dcc.Dropdown(
                            id='trend-view-filter',
                            options=[
                                {'label': 'Average 24-Hour Trend', 'value': 'average'},
                                *[
                                    {'label': str(date), 'value': str(date)}
                                    for date in sorted(df['timestamp'].dt.date.unique()) if not df.empty
                                ]
                            ],
                            value='average',
                            placeholder="Select Trend View",
                            style={
                                'width': '100%', 
                                'fontSize': '12px', 
                                'borderRadius': '4px', 
                                'border': '1px solid #ced4da',
                                'backgroundColor': '#ffffff',
                                'height': '30px'
                            },
                            className="shadow-sm"
                        )
                    ], width=2, className="p-1"),
                    # Reset
                    dbc.Col([
                        html.Label("Reset", style={'color': '#34495e', 'fontSize': '12px', 'visibility': 'hidden'}),
                        dbc.Button(
                            "Reset",
                            id='reset-button',
                            color='primary',
                            className='w-100 shadow-sm',
                            style={'borderRadius': '4px', 'fontSize': '12px', 'height': '30px', 'padding': '0 10px'}
                        )
                    ], width=1, className="p-1")
                ], style={'gap': '10px', 'alignItems': 'center'}),
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '10px',
                'borderRadius': '6px',
                'boxShadow': '0 1px 4px rgba(0, 0, 0, 0.05)',
                'border': '1px solid #e9ecef'
            })
        ], width=12, className="offset-md-0")
    ], className="mb-3"),
    
    # Main Content
    dbc.Row([
        dbc.Col([
            # KPI Metric Cards
            dcc.Loading([
                dbc.Row(id='kpi-cards', className="mb-4", style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center', 'gap': '15px'}),
            ], type='circle'),
            # Summary Statistics Table and Download Button
            dcc.Loading([
                dbc.Row([
                    dbc.Col([
                        html.H4("Daily Request Volume Summary Statistics", className="text-center mb-3", style={'color': '#2c3e50', 'fontSize': '20px'}),
                        html.Div(id='summary-stats-table', className="mb-3"),
                        dbc.Button(
                            "Download Summary Report",
                            id='download-button',
                            color='success',
                            className='w-100 shadow-sm mb-3',
                            style={'borderRadius': '4px', 'fontSize': '12px', 'height': '30px', 'padding': '0 10px'}
                        ),
                        dcc.Download(id='download-dataframe')
                    ], width=12)
                ], className="mb-4")
            ]),
            # Visualizations
            dcc.Loading([
                dbc.Row([
                    dbc.Col(dcc.Graph(id='revenue-bar'), width=6),
                    dbc.Col(dcc.Graph(id='request-pie'), width=6),
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='job-type-bar'), width=6),
                    dbc.Col(dcc.Graph(id='affiliate-bar', style={'height': '400px'}), width=6),
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='revenue-map'), width=12),
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='trend-graph'), width=12),
                ], className="mb-4"),
            ]),
            html.Div(id='error-message', className="text-danger text-center mt-2")
        ], width=12)
    ]),
    dcc.Store(id='filtered-data')
], fluid=True, style={'padding': '0', 'backgroundColor': '#f8f9fa'})

# Update country filter based on continent
@app.callback(
    Output('country-filter', 'options'),
    Input('continent-filter', 'value')
)
def update_country_filter(continent):
    if not continent or df.empty:
        return [{'label': c, 'value': c} for c in sorted(df['country'].unique())] if not df.empty else []
    countries = sorted(continent_countries.get(continent, []))
    return [{'label': c, 'value': c} for c in countries]

# Download callback
@app.callback(
    Output('download-dataframe', 'data'),
    Input('download-button', 'n_clicks'),
    State('filtered-data', 'data'),
    prevent_initial_call=True
)
def download_report(n_clicks, filtered_data):
    if not filtered_data:
        return None
    try:
        filtered_df = pd.DataFrame(filtered_data)
        filtered_df['date'] = pd.to_datetime(filtered_df['timestamp']).dt.date
        stats_data = filtered_df.groupby(['date', 'request_type']).size().unstack(fill_value=0).reset_index()
        job_placement_data = filtered_df[filtered_df['job_type'] != 'None'].groupby('date').size().reset_index(name='job_placements')
        stats_data = stats_data.merge(job_placement_data, on='date', how='left').fillna(0)
        stats_data['promo'] = stats_data.get('promo', pd.Series(0, index=stats_data.index))
        stats_data['demo'] = stats_data.get('demo', pd.Series(0, index=stats_data.index))
        stats_data['ai_assist'] = stats_data.get('ai_assist', pd.Series(0, index=stats_data.index))
        
        summary_stats = pd.DataFrame({
            'Metric': ['Demo Requests', 'AI Assist Requests', 'Promo Events', 'Job Placements'],
            'Mean': [
                stats_data['demo'].mean(),
                stats_data['ai_assist'].mean(),
                stats_data['promo'].mean(),
                stats_data['job_placements'].mean()
            ],
            'Median': [
                stats_data['demo'].median(),
                stats_data['ai_assist'].median(),
                stats_data['promo'].median(),
                stats_data['job_placements'].median()
            ],
            'Standard Deviation': [
                stats_data['demo'].std(),
                stats_data['ai_assist'].std(),
                stats_data['promo'].std(),
                stats_data['job_placements'].std()
            ]
        })
        
        return dcc.send_data_frame(summary_stats.to_csv, f"summary_stats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    except Exception as e:
        logger.error(f"Download callback error: {str(e)}")
        return None

# Main callback
@app.callback(
    [
        Output('kpi-cards', 'children'),
        Output('revenue-bar', 'figure'),
        Output('request-pie', 'figure'),
        Output('job-type-bar', 'figure'),
        Output('affiliate-bar', 'figure'),
        Output('revenue-map', 'figure'),
        Output('trend-graph', 'figure'),
        Output('filtered-data', 'data'),
        Output('error-message', 'children'),
        Output('continent-filter', 'value'),
        Output('country-filter', 'value'),
        Output('product-filter', 'value'),
        Output('date-filter', 'start_date'),
        Output('date-filter', 'end_date'),
        Output('summary-stats-table', 'children')
    ],
    [
        Input('continent-filter', 'value'),
        Input('country-filter', 'value'),
        Input('product-filter', 'value'),
        Input('date-filter', 'start_date'),
        Input('date-filter', 'end_date'),
        Input('reset-button', 'n_clicks'),
        Input('trend-view-filter', 'value')
    ],
    prevent_initial_call=False
)
def update_dashboard(continent, countries, products, start_date, end_date, reset_clicks, trend_view):
    ctx = callback_context
    filtered_df = df.copy() if not df.empty else pd.DataFrame()
    
    # Handle reset
    if ctx.triggered_id == 'reset-button':
        continent = None
        countries = []
        products = []
        start_date = min_date
        end_date = max_date
        trend_view = 'average'
    
    try:
        # Apply filters
        if continent:
            filtered_df = filtered_df[filtered_df['continent'] == continent]
        if countries:
            filtered_df = filtered_df[filtered_df['country'].isin(countries)]
        if products:
            filtered_df = filtered_df[filtered_df['product_type'].isin(products)]
        if start_date and end_date:
            try:
                start_date = pd.to_datetime(start_date).date()
                end_date = pd.to_datetime(end_date).date()
                filtered_df = filtered_df[
                    (filtered_df['timestamp'].dt.date >= start_date) & 
                    (filtered_df['timestamp'].dt.date <= end_date)
                ]
            except Exception as e:
                logger.error(f"Date filter error: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.update_layout(title="Invalid Date Range", showlegend=False, template="plotly_white")
                return (
                    [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                    [], "Invalid date range selected",
                    None, [], [], min_date, max_date, []
                )
        
        # Check for empty data
        if filtered_df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="No Data Available", showlegend=False, template="plotly_white")
            return (
                [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                [], "No data available for selected filters",
                None, [], [], min_date, max_date, []
            )
        
        # KPIs
        total_revenue = filtered_df['revenue ($)'].sum()
        total_interactions = len(filtered_df)
        purchases = filtered_df['purchase_flag'].sum()
        conversion_rate = (purchases / total_interactions * 100) if total_interactions > 0 else 0
        demo_count = len(filtered_df[filtered_df['request_type'] == 'demo'])
        demo_purchases = len(filtered_df[(filtered_df['request_type'] == 'demo') & (filtered_df['purchase_flag'] == 1)])
        demo_rate = (demo_purchases / demo_count * 100) if demo_count > 0 else 0
        jobs_placed = len(filtered_df[filtered_df['job_type'] != 'None'])
        ai_assist_requests = len(filtered_df[filtered_df['request_type'] == 'ai_assist'])
        promo_requests = len(filtered_df[filtered_df['request_type'] == 'promo'])
        
        # Helper function to create metric card
        def create_metric_card(title, value, target, unit, format_value):
            status = 'success' if value >= target * 0.9 else 'warning' if value >= target * 0.7 else 'danger'
            return dbc.Card([
                dbc.CardBody([
                    html.H6(title, className="card-title text-center mb-2"),
                    html.H3(
                        f"{format_value(value)}{unit}",
                        className=f"text-{status} text-center mb-1",
                        style={'fontWeight': 'bold', 'fontSize': '24px'}
                    ),
                    html.P(
                        f"Target: {format_value(target)}{unit}",
                        className="card-text text-center text-muted mb-0",
                        style={'fontSize': '14px'}
                    ),
                    html.P(
                        f"Status: {'On Track' if status == 'success' else 'Needs Attention' if status == 'warning' else 'Below Target'}",
                        className=f"text-{status} text-center mb-0",
                        style={'fontSize': '14px'}
                    )
                ])
            ], className=f"border-{status} mb-3", style={'width': '180px', 'height': '180px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})

        # KPI Cards
        kpi_cards = [
            create_metric_card("Revenue", total_revenue, TARGETS['revenue'], "$", lambda x: f"{x:,.0f}"),
            create_metric_card("Conversion Rate", conversion_rate, TARGETS['conversion_rate'], "%", lambda x: f"{x:.1f}"),
            create_metric_card("Demo-to-Purchase", demo_rate, TARGETS['demo_to_purchase'], "%", lambda x: f"{x:.1f}"),
            create_metric_card("Jobs Placed", jobs_placed, TARGETS['jobs_placed'], "", lambda x: f"{x:,.0f}"),
            create_metric_card("AI Assist Requests", ai_assist_requests, TARGETS['ai_assist_requests'], "", lambda x: f"{x:,.0f}"),
            create_metric_card("Promo Requests", promo_requests, TARGETS['promo_requests'], "", lambda x: f"{x:,.0f}")
        ]
        
        # Summary Statistics
        filtered_df['date'] = filtered_df['timestamp'].dt.date
        stats_data = filtered_df.groupby(['date', 'request_type']).size().unstack(fill_value=0).reset_index()
        job_placement_data = filtered_df[filtered_df['job_type'] != 'None'].groupby('date').size().reset_index(name='job_placements')
        stats_data = stats_data.merge(job_placement_data, on='date', how='left').fillna(0)
        stats_data['promo'] = stats_data.get('promo', pd.Series(0, index=stats_data.index))
        stats_data['demo'] = stats_data.get('demo', pd.Series(0, index=stats_data.index))
        stats_data['ai_assist'] = stats_data.get('ai_assist', pd.Series(0, index=stats_data.index))
        
        summary_stats = pd.DataFrame({
            'Metric': ['Demo Requests', 'AI Assist Requests', 'Promo Events', 'Job Placements'],
            'Mean': [
                stats_data['demo'].mean(),
                stats_data['ai_assist'].mean(),
                stats_data['promo'].mean(),
                stats_data['job_placements'].mean()
            ],
            'Median': [
                stats_data['demo'].median(),
                stats_data['ai_assist'].median(),
                stats_data['promo'].median(),
                stats_data['job_placements'].median()
            ],
            'Standard Deviation': [
                stats_data['demo'].std(),
                stats_data['ai_assist'].std(),
                stats_data['promo'].std(),
                stats_data['job_placements'].std()
            ]
        })
        
        summary_stats['Mean'] = summary_stats['Mean'].round(2)
        summary_stats['Median'] = summary_stats['Median'].round(2)
        summary_stats['Standard Deviation'] = summary_stats['Standard Deviation'].round(2)
        
        stats_table = dbc.Table.from_dataframe(
            summary_stats,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            style={
                'fontSize': '12px',
                'textAlign': 'center',
                'borderRadius': '4px',
                'boxShadow': '0 1px 4px rgba(0, 0, 0, 0.05)'
            }
        )
        
        # Revenue Bar
        revenue_data = filtered_df.groupby('salesperson_id')['revenue ($)'].sum().reset_index()
        revenue_data['target'] = TARGETS['revenue']
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=revenue_data['salesperson_id'],
            y=revenue_data['revenue ($)'],
            name='Revenue ($)',
            marker_color='#007bff'
        ))
        fig_bar.add_trace(go.Scatter(
            x=revenue_data['salesperson_id'],
            y=revenue_data['target'],
            name='Target',
            mode='lines+markers',
            line=dict(color='red', dash='dash')
        ))
        fig_bar.update_layout(
            title="Revenue by Salesperson",
            yaxis_title="Revenue ($)",
            template="plotly_white",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        # Request Type Pie
        request_dist = filtered_df['request_type'].value_counts().reset_index()
        request_dist.columns = ['request_type', 'count']
        fig_pie = px.pie(
            request_dist,
            names='request_type',
            values='count',
            title='Request Type Distribution',
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_white"
        )
        fig_pie.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        
        # Job Type Bar
        job_types = filtered_df[filtered_df['job_type'] != 'None']['job_type'].value_counts().reset_index()
        job_types.columns = ['job_type', 'count']
        fig_job = px.bar(
            job_types,
            x='job_type',
            y='count',
            title='Jobs by Type',
            labels={'job_type': 'Job Type', 'count': 'Count'},
            color_discrete_sequence=['#28a745'],
            template="plotly_white"
        )
        fig_job.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        
        # Affiliate Code Bar
        affiliate_data = filtered_df.groupby('affiliate_code')['revenue ($)'].sum().reset_index()
        affiliate_data = affiliate_data[affiliate_data['affiliate_code'] != 'None']
        fig_affiliate = px.bar(
            affiliate_data,
            x='affiliate_code',
            y='revenue ($)',
            title='Revenue by Marketing Channel (Affiliate Code)',
            labels={'affiliate_code': 'Affiliate Code', 'revenue ($)': 'Revenue ($)'},
            color_discrete_sequence=['#ff9900'],
            template="plotly_white"
        )
        fig_affiliate.update_layout(margin=dict(l=40, r=40, t=40, b=40))
        
        # Revenue Map
        revenue_by_country = filtered_df.groupby('country')['revenue ($)'].sum().reset_index()
        fig_map = px.choropleth(
            revenue_by_country,
            locations='country',
            locationmode='country names',
            color='revenue ($)',
            title='Revenue by Country',
            color_continuous_scale='Blues',
            scope=continent.lower() if continent else 'world',
            template="plotly_white"
        )
        fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True), margin=dict(l=40, r=40, t=40, b=40))
        
        # Trend Graph (Hourly and 24-Hour Basis)
        filtered_df['hour'] = filtered_df['timestamp'].dt.hour
        if trend_view == 'average':
            # Aggregate by hour across all days
            trend_data = filtered_df.groupby(['hour', 'request_type']).size().unstack(fill_value=0).reset_index()
            job_placement_data = filtered_df[filtered_df['job_type'] != 'None'].groupby('hour').size().reset_index(name='job_placements')
            trend_data = trend_data.merge(job_placement_data, on='hour', how='left').fillna(0)
            title = 'Average Hourly Trends: Promo, Demo, AI Assist, and Job Placements'
        else:
            # Filter for the specific date
            selected_date = pd.to_datetime(trend_view).date()
            trend_data = filtered_df[filtered_df['timestamp'].dt.date == selected_date]
            trend_data = trend_data.groupby(['hour', 'request_type']).size().unstack(fill_value=0).reset_index()
            job_placement_data = filtered_df[(filtered_df['timestamp'].dt.date == selected_date) & (filtered_df['job_type'] != 'None')].groupby('hour').size().reset_index(name='job_placements')
            trend_data = trend_data.merge(job_placement_data, on='hour', how='left').fillna(0)
            title = f'Hourly Trends on {selected_date}: Promo, Demo, AI Assist, and Job Placements'
        
        # Ensure all hours (0–23) are present
        all_hours = pd.DataFrame({'hour': range(24)})
        trend_data = all_hours.merge(trend_data, on='hour', how='left').fillna(0)
        trend_data['promo'] = trend_data.get('promo', pd.Series(0, index=trend_data.index))
        trend_data['demo'] = trend_data.get('demo', pd.Series(0, index=trend_data.index))
        trend_data['ai_assist'] = trend_data.get('ai_assist', pd.Series(0, index=trend_data.index))
        trend_data['job_placements'] = trend_data.get('job_placements', pd.Series(0, index=trend_data.index))
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_data['hour'],
            y=trend_data['promo'],
            name='Promo Events',
            mode='lines+markers',
            line=dict(color='#ff9900')
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_data['hour'],
            y=trend_data['demo'],
            name='Demo Requests',
            mode='lines+markers',
            line=dict(color='#007bff')
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_data['hour'],
            y=trend_data['ai_assist'],
            name='AI Assist Usage',
            mode='lines+markers',
            line=dict(color='#28a745')
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_data['hour'],
            y=trend_data['job_placements'],
            name='Job Placements',
            mode='lines+markers',
            line=dict(color='#dc3545')
        ))
        fig_trend.update_layout(
            title=title,
            xaxis_title='Hour of Day',
            yaxis_title='Count',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(24)),
                ticktext=[f"{h:02d}:00" for h in range(24)]
            ),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            template="plotly_white",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return (
            kpi_cards,
            fig_bar, fig_pie, fig_job, fig_affiliate, fig_map, fig_trend,
            filtered_df.to_dict('records'), "",
            continent, countries, products, start_date, end_date,
            stats_table
        )
    
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Error Occurred", showlegend=False, template="plotly_white")
        return (
            [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
            [], f"Error updating dashboard: {str(e)}",
            None, [], [], min_date, max_date, []
        )

if __name__ == '__main__':
    app.run(debug=True)


app = dash.Dash(__name__)
server = app.server
