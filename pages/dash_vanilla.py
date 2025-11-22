from dash import Dash, html, dcc, callback, Output, Input
import dash
import pandas as pd
import geopandas as gpd
import plotly.express as px

dash.register_page(__name__, path="/")

df = pd.read_csv('data/TB_Burden_Country.csv')
world_map = gpd.read_file(
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_countries.geojson"
)

df['Year'] = pd.to_datetime(df['Year'], format='%Y')

layout = html.Div([
    html.H1('Global Tuberculosis Dashboard', style={'textAlign': 'center'}),

    dcc.Link(html.Button("Bootstrap"), href="/bootstrap", refresh=False),


    html.Div([
        html.Div([
            html.Label('Select Countries:'),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in df['Country or territory name'].unique()],
                value=['Afghanistan', 'India'],
                multi=True,
                searchable=True
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),

        html.Div([
            html.Label('Select Region:'),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': r, 'value': r} for r in df['Region'].unique()],
                value='EUR',
                searchable=True
            )
        ], style={'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'})
    ], style={'padding': '10px 0'}),

html.Div([
            html.Label('Select Year:'),
            dcc.Slider(
                id='year-slider',
                min=int(df['Year'].dt.year.min()),
                max=int(df['Year'].dt.year.max()),
                step=1,
                value=int(df['Year'].dt.year.min()),
                marks={int(y): str(int(y)) for y in df['Year'].dt.year.unique()},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={"width": "100%", 'verticalAlign': 'top', 'padding': '10px 0'}),

    dcc.Tabs([
        dcc.Tab(label='Country Trends', children=[
            html.Div([
                dcc.Graph(id='tb-prevalence-chart', style={'height': '600px', 'display': 'inline-block', 'width': '49%'}),
                dcc.Graph(id='tb-prevalence-vs-mortality', style={'height': '600px', 'display': 'inline-block', 'width': '49%'})
            ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'space-between'})
        ]),
        dcc.Tab(label='Regional Trends', children=[
            dcc.Graph(id='tb-incidence-by-region', style={'height': '600px'})
        ]),
        dcc.Tab(label='Global Overview', children=[
            html.Div([
                dcc.Graph(id='tb-global-map', style={'height': '600px', 'display': 'inline-block', 'width': '49%'}),
                dcc.Graph(id='tb-top10', style={'height': '600px', 'display': 'inline-block', 'width': '49%'})
            ], style={'width': '100%', 'display': 'flex', 'justifyContent': 'space-between'})
        ])
    ])
], style={'width': '95%', 'margin': '0 auto', 'fontFamily': 'Arial'})

@callback(
    Output('tb-prevalence-chart', 'figure'),
    Input('country-dropdown', 'value')
)
def update_chart(selected_countries):
    filtered_df = df[df['Country or territory name'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='Estimated prevalence of TB (all forms) per 100 000 population',
                 color='Country or territory name', title=f'TB Prevalence Over Time in Selected Countries')
    return fig

@callback(
    Output('tb-prevalence-vs-mortality', 'figure'),
    Input('country-dropdown', 'value')
)
def update_prevalence_vs_mortality(selected_countries):
    filtered_df = df[df['Country or territory name'].isin(selected_countries)]
    fig = px.scatter(filtered_df, x='Estimated prevalence of TB (all forms) per 100 000 population',
                     y='Estimated mortality of TB cases (all forms, excluding HIV) per 100 000 population',
                     color='Country or territory name',
                     title=f'TB Prevalence vs. Mortality in Selected Countries')
    return fig


@callback(
    Output('tb-incidence-by-region', 'figure'),
    Input('region-dropdown', 'value')
)
def update_incidence_by_region(selected_region):
    filtered_df = df[df['Region'] == selected_region]
    fig = px.line(filtered_df, x='Year', y='Estimated incidence (all forms) per 100 000 population',
                 title=f'TB Incidence Over Time in {selected_region}')
    return fig

@callback(
    Output('tb-global-map', 'figure'),
    Input('year-slider', 'value')
)
def update_global_map(selected_year):
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
        title=f"Global TB Prevalence ({selected_year})"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    return fig

@callback(
    Output('tb-top10', 'figure'),
    Input('year-slider', 'value')
)
def update_top10(year):
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
        title=f'Top 10 Countries with Highest TB Prevalence ({year})'
    )
    return fig