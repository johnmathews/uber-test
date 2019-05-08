# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import json
from datetime import timedelta as td
from datetime import datetime
import pandas as pd
import numpy as np

# import data
df = pd.read_csv('uber-data.csv', infer_datetime_format=True, parse_dates=[0])
df.week_start = pd.to_datetime(df.week_start, infer_datetime_format=True)
df = df.sort_values(by='week_start', ascending=True)

available_metrics = df.columns[5:]
available_dates = [np.datetime64(x, 'D') for x in  df.week_start.unique()]
available_regions = df[df.region_x != 'EMEA'].region_x.unique()

# reusable components
def total_of_metric(region, metric, week):
    if region == 'EMEA':
        result = df[df.week_start == week][[metric]].sum().item()
    else:
        result = df[(df.week_start == week) & (df.region_x == region)][[metric]].sum().item()
    return f"total: {result:,}"

def metric_change_week_on_week(region, metric, week):
    current_week = datetime.strptime(week, '%Y-%m-%d')
    previous_week = current_week - td(days=7)
    if region == 'EMEA':
        weekly_total = df[df.week_start == current_week][[metric]].sum().item()
        previous_weekly_total = df[df.week_start == previous_week][[metric]].sum().item()
        change = 100 * ((weekly_total - previous_weekly_total) / previous_weekly_total)
    else:
        weekly_total = df[(df.week_start == current_week) & (df.region_x == region)][[metric]].sum().item()
        previous_weekly_total = df[(df.week_start == previous_week) & (df.region_x == region)][[metric]].sum().item()
        change = 100 * ((weekly_total - previous_weekly_total) / previous_weekly_total)
    return f"change: {round(change,2)}%"


app = dash.Dash(__name__,  meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

# styling
colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

region_heading_style = {
    'margin': 5,
    'padding': 5,
    'width': '25%',
    'display': 'flex',
    'flex-direction': 'row',
    'backgroundColor': colors['background'],
    'color': colors['text'],
    'textAlign': 'center',
    'borderRadius': 3
}

total_style_dict = {
    'margin': 5,
    'padding': 5,
    'width': '12.5%',
    'display': 'flex',
    'flex-direction': 'row',
    'backgroundColor': colors['background'],
    'color': colors['text'],
    'textAlign': 'center',
    'borderRadius': 3,
}

dropdown_style = {
    'margin-left': '2%',
    'margin-right': '2%',
    'position': 'relative',
    'align': 'center',
    'display': 'inline',
}

# page structure - uses flexbox for responsive design
app.layout = html.Div([

    ## menues to select metric and week
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='metrics_dropdown',
                options=[{'label': i.replace('_', ' ').title(), 'value': i} for i in available_metrics],
                value=available_metrics[0],
                clearable=False,
            ),
            style=dropdown_style
        ),
        html.Div(
            dcc.Dropdown(
                id='dates_dropdown',
                options=[{'label': i, 'value': i} for i in available_dates],
                clearable=False,
                value=available_dates[-1]
            ),
            style=dropdown_style
        ),
    ], style={'display':'flex', 'flexDirection': 'column', 'width':'12.5%', 'margin-left': 'auto'}),

    ## region/subregion titles
    html.Div([
        html.Div( children='EMEA', style=region_heading_style),
        html.Div( children='MEA', style=region_heading_style),
        html.Div( children='WSE', style=region_heading_style),
        html.Div( children='NEE', style=region_heading_style),
    ], style={'display':'flex', 'flexDirection': 'row'}),

    ## metric totals and metric weekly change
    html.Div([
        html.Div( id='EMEA_change', children='start', style=total_style_dict),
        html.Div( id='EMEA_total', children='start', style=total_style_dict),
        html.Div( id='MEA_change', children='start', style=total_style_dict),
        html.Div( id='MEA_total', children='start', style=total_style_dict),
        html.Div( id='WSE_change', children='start', style=total_style_dict),
        html.Div( id='WSE_total', children='start', style=total_style_dict),
        html.Div( id='NEE_change', children='start', style=total_style_dict),
        html.Div( id='NEE_total', children='start', style=total_style_dict),
    ], style={'display':'flex', 'flexDirection': 'row'}),

    ## line charts
    html.Div([
        html.Div([
            dcc.Graph(id="regions", config={'displayModeBar': False}),
            ]),
        html.Div([
            dcc.Graph(id="sub-regions", config={'displayModeBar': False}),
            ])
    ], style={'display':'flex', 'flexDirection': 'row'})

], style={'display':'flex', 'flexDirection': 'column'})

# callbacks for interactive features
## totals and weekly change for selected metric and week
@app.callback(
    Output(component_id='EMEA_total', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return total_of_metric('EMEA', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='EMEA_change', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return metric_change_week_on_week('EMEA', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='MEA_total', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return total_of_metric('EMEA - MEA', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='MEA_change', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return metric_change_week_on_week('EMEA - MEA', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='WSE_total', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return total_of_metric('EMEA - WSE', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='WSE_change', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return metric_change_week_on_week('EMEA - WSE', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='NEE_total', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return total_of_metric('EMEA - NEE', metrics_dropdown, dates_dropdown)

@app.callback(
    Output(component_id='NEE_change', component_property='children'),
    [Input(component_id='dates_dropdown', component_property='value'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_output_div(dates_dropdown, metrics_dropdown):
    return metric_change_week_on_week('EMEA - NEE', metrics_dropdown, dates_dropdown)

## region line chart
@app.callback(
    Output(component_id='regions', component_property='figure'),
    [Input(component_id='metrics_dropdown', component_property='value')]
)
def update_figure(selected_metric):
    regions = df[df.region_x != 'EMEA'].region_x.unique()
    traces = []

    for region in regions:
        filtered_data_frame = df[df.region_x == region][['week_start', selected_metric]].groupby('week_start').agg('sum').reset_index()
        traces.append(go.Scatter(
            x = filtered_data_frame.week_start,
            y = filtered_data_frame[selected_metric],
            name = region[6:]
        ))


    return {'data': traces, 'layout': go.Layout(title=selected_metric.replace('_', ' ').title(), autosize=True, hovermode='closest', legend={'orientation':'h'},)}

## sub-region line chart
@app.callback(
    Output(component_id='sub-regions', component_property='figure'),
    [Input(component_id='regions', component_property='hoverData'),
     Input(component_id='metrics_dropdown', component_property='value')]
)
def update_figure(hoverData, selected_metric):
    if hoverData:
        region = hoverData['points'][0]['curveNumber']
    else:
        region = 0

    region = available_regions[region]
    sub_regions = df[df.region_x == region].sub_region_x.unique()
    traces = []

    for sub_region in sub_regions:
        filtered_data_frame = df[df.sub_region_x == sub_region][['week_start', selected_metric]].groupby('week_start').agg('sum').reset_index()
        traces.append(go.Scatter(
            x = filtered_data_frame.week_start,
            y = filtered_data_frame[selected_metric],
            name = sub_region
        ))


    return {'data': traces, 'layout': go.Layout(title=region[6:] + f': {selected_metric}'.replace('_', ' '), autosize=True, legend={'orientation':'h'})}


if __name__ == '__main__':
    app.run_server(debug=False)
