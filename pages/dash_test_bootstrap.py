import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import plotly.express as px

dash.register_page(__name__, path="/bootstrap")
df = pd.read_csv('data/TB_Burden_Country.csv')
df['Year'] = pd.to_datetime(df['Year'], format='%Y')
world_map = gpd.read_file(
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
)

layout = dbc.Container([
    dbc.Row([
        dbc.Col(dbc.Button(
            "Vanilla",
            href="/",
            color="White",
        )),
        dbc.Col([
            html.H1('Global Tuberculosis Dashboard',
                    className='text-center my-4 display-4 fw-bold',
                    style={'color': '#2c3e50', 'letterSpacing': '0.5px'})
        ], width=12)
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Country Selection", className='fw-bold bg-light'),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='country-dropdown_bootstrap',
                        options=[{'label': c, 'value': c} for c in df['Country or territory name'].unique()],
                        value=['Afghanistan', 'India'],
                        multi=True,
                        searchable=True,
                        className='mb-2'
                    )
                ])
            ], className='h-100 shadow-sm')
        ], lg=4, md=6, className='mb-3'),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Region Selection", className='fw-bold bg-light'),
                dbc.CardBody([
                    dcc.Dropdown(
                        id='region-dropdown_bootstrap',
                        options=[{'label': r, 'value': r} for r in df['Region'].unique()],
                        value='EUR',
                        searchable=True,
                        className='mb-2'
                    )
                ])
            ], className='h-100 shadow-sm')
        ], lg=4, md=6, className='mb-3'),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Year Selection", className='fw-bold bg-light'),
                dbc.CardBody([
                    html.Div([
                        dcc.Slider(
                            id='year-slider_bootstrap',
                            min=int(df['Year'].dt.year.min()),
                            max=int(df['Year'].dt.year.max()),
                            step=1,
                            value=int(df['Year'].dt.year.min()),
                            marks={int(y): {'label': str(int(y)), 'style': {'transform': 'rotate(45deg)'}}
                                   for y in df['Year'].dt.year.unique() if int(y) % 5 == 0},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'padding': '20px 10px 0px 10px'})
                ])
            ], className='h-100 shadow-sm')
        ], lg=4, md=12, className='mb-3')
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Tabs([
                        dcc.Tab(
                            label="Country Trends",
                            children=[
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("TB Prevalence Over Time", className='fw-bold'),
                                            dbc.CardBody([
                                                dcc.Graph(id='tb-prevalence-chart_bootstrap')
                                            ])
                                        ], className='shadow-sm border-0')
                                    ], lg=6, className='mb-3'),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Prevalence vs Mortality", className='fw-bold'),
                                            dbc.CardBody([
                                                dcc.Graph(id='tb-prevalence-vs-mortality_bootstrap')
                                            ])
                                        ], className='shadow-sm border-0')
                                    ], lg=6, className='mb-3')
                                ])
                            ],
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),

                        dcc.Tab(
                            label="Regional Trends",
                            children=[
                                dbc.Card([
                                    dbc.CardHeader("TB Incidence by Region", className='fw-bold'),
                                    dbc.CardBody([
                                        dcc.Graph(id='tb-incidence-by-region_bootstrap')
                                    ])
                                ], className='shadow-sm border-0')
                            ]
                        ),

                        dcc.Tab(
                            label= "Global Overview",
                            children=[
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Global TB Prevalence Map", className='fw-bold'),
                                            dbc.CardBody([
                                                dcc.Graph(id='tb-global-map_bootstrap')
                                            ])
                                        ], className='shadow-sm border-0')
                                    ], lg=6, className='mb-3'),
                                    dbc.Col([
                                        dbc.Card([
                                            dbc.CardHeader("Top 10 Countries by Prevalence", className='fw-bold'),
                                            dbc.CardBody([
                                                dcc.Graph(id='tb-top10_bootstrap')
                                            ])
                                        ], className='shadow-sm border-0')
                                    ], lg=6, className='mb-3')
                                ])
                            ]
                        )
                    ], colors={
                        "border": "white",
                        "primary": "#2c3e50",
                        "background": "#f8f9fa"
                    })
                ])
            ], className='shadow border-0')
        ], width=12)
    ])
], fluid=True, style={'fontFamily': 'Georgia, serif', 'backgroundColor': 'white'})

custom_css = """
.custom-tab {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-bottom: none;
    padding: 12px 24px;
    margin-right: 4px;
    border-radius: 4px 4px 0 0;
    font-weight: 500;
}

.custom-tab--selected {
    background-color: white !important;
    border-color: #dee2e6;
    border-bottom: 2px solid #2c3e50;
    color: #2c3e50;
    font-weight: 600;
}

.card {
    border-radius: 8px;
}

.shadow-sm {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important;
}
"""


@callback(
    Output('tb-prevalence-chart_bootstrap', 'figure'),
    Input('country-dropdown_bootstrap', 'value')
)
def update_chart_bootstrap(selected_countries):
    filtered_df = df[df['Country or territory name'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='Estimated prevalence of TB (all forms) per 100 000 population',
                  color='Country or territory name',
                  title='',
                  template='plotly_white')
    fig.update_layout(
        font_family="Georgia, serif",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig


@callback(
    Output('tb-prevalence-vs-mortality_bootstrap', 'figure'),
    Input('country-dropdown_bootstrap', 'value')
)
def update_prevalence_vs_mortality_bootstrap(selected_countries):
    filtered_df = df[df['Country or territory name'].isin(selected_countries)]
    fig = px.scatter(filtered_df,
                     x='Estimated prevalence of TB (all forms) per 100 000 population',
                     y='Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population',
                     color='Country or territory name',
                     title='',
                     template='plotly_white')
    fig.update_layout(
        font_family="Georgia, serif",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig


@callback(
    Output('tb-incidence-by-region_bootstrap', 'figure'),
    Input('region-dropdown_bootstrap', 'value')
)
def update_incidence_by_region_bootstrap(selected_region):
    filtered_df = df[df['Region'] == selected_region]
    fig = px.line(filtered_df, x='Year', y='Estimated incidence (all forms) per 100 000 population',
                  title='', template='plotly_white')
    fig.update_layout(
        font_family="Georgia, serif",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig


@callback(
    Output('tb-global-map_bootstrap', 'figure'),
    Input('year-slider_bootstrap', 'value')
)
def update_global_map_bootstrap(selected_year):
    df_year = df[df['Year'].dt.year == selected_year]

    merged = world_map.merge(
        df_year,
        left_on='name_long',
        right_on='Country or territory name',
        how='left'
    )

    fig = px.choropleth(
        merged,
        geojson=merged.geometry.__geo_interface__,
        locations=merged.index,
        color='Estimated prevalence of TB (all forms) per 100 000 population',
        projection="natural earth",
        title="",
        template='plotly_white',
        color_continuous_scale='Blues'
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        font_family="Georgia, serif",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig


@callback(
    Output('tb-top10_bootstrap', 'figure'),
    Input('year-slider_bootstrap', 'value')
)
def update_top10_bootstrap(year):
    subset = df[df['Year'].dt.year == year].copy()
    subset = subset.sort_values(
        'Estimated prevalence of TB (all forms) per 100 000 population',
        ascending=False
    ).head(10)

    fig = px.bar(
        subset,
        x='Estimated prevalence of TB (all forms) per 100 000 population',
        y='Country or territory name',
        orientation='h',
        title='',
        template='plotly_white',
        color='Estimated prevalence of TB (all forms) per 100 000 population',
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        font_family="Georgia, serif",
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False
    )
    return fig