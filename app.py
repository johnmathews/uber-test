# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from datetime import timedelta as td
from datetime import datetime
import pandas as pd
import numpy as np

df = pd.read_csv('uber-data.csv', infer_datetime_format=True, parse_dates=[0])
df.week_start = pd.to_datetime(df.week_start, infer_datetime_format=True)
df = df.sort_values(by='week_start', ascending=True)

available_metrics = df.columns[5:]
available_dates = [np.datetime64(x, 'D') for x in  df.week_start.unique()]

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
        if weekly_total == 0 or previous_weekly_total == 0:
            change = 'placeholder'
        else:
            change = round((weekly_total - previous_weekly_total) / previous_weekly_total,2)
    else:
        weekly_total = df[(df.week_start == current_week) & (df.region_x == region)][[metric]].sum().item()
        previous_weekly_total = df[(df.week_start == previous_week) & (df.region_x == region)][[metric]].sum().item()
        if weekly_total == 0 or previous_weekly_total == 0:
            change = 'placeholder'
        else:
            change = round((weekly_total - previous_weekly_total) / previous_weekly_total,2)
    return f"change: {change}%"


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

region_width = '22%'
sub_total_width = '11%'

container_style = {
    'maxWidth': 1000,
}

region_heading_style = {
    'margin': 5,
    'padding': 5,
    'width': region_width,
    'display': 'inline-block',
    'backgroundColor': colors['background'],
    'color': colors['text'],
    'textAlign': 'center',
}

total_style_dict = {
    'margin': 5,
    'padding': 5,
    'width': sub_total_width,
    'display': 'inline-block',
    'backgroundColor': colors['background'],
    'color': colors['text'],
    'textAlign': 'center'
}

dropdown_style = {
    'margin-left': 'auto',
    'position': 'relative',
    'width': 200,
    'align': 'right',
}


app.layout = html.Div([

    html.Div([
        html.Div(
            dcc.Dropdown(
                id='metrics_dropdown',
                options=[{'label': i, 'value': i} for i in available_metrics],
                value=available_metrics[0],
                clearable=False,
                style=dropdown_style
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
    ]),

    html.Div([
        html.Div( children='EMEA', style=region_heading_style),
        html.Div( children='MEA', style=region_heading_style),
        html.Div( children='WSE', style=region_heading_style),
        html.Div( children='NEE', style=region_heading_style),
    ]),
    html.Div([
        html.Div( id='EMEA_change', children='start', style=total_style_dict),
        html.Div( id='EMEA_total', children='start', style=total_style_dict),
        html.Div( id='MEA_change', children='start', style=total_style_dict),
        html.Div( id='MEA_total', children='start', style=total_style_dict),
        html.Div( id='WSE_change', children='start', style=total_style_dict),
        html.Div( id='WSE_total', children='start', style=total_style_dict),
        html.Div( id='NEE_change', children='start', style=total_style_dict),
        html.Div( id='NEE_total', children='start', style=total_style_dict),
    ]),
    html.Div([
        dcc.Graph(id="figure-1")
    ])
])

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

@app.callback(
    Output(component_id='figure-1', component_property='figure'),
    [Input(component_id='metrics_dropdown', component_property='value')]
)
def update_figure(selected_metric):
    regions = df[df.region_x != 'EMEA'].region_x.unique()
    filtered_data_frames = {}
    traces = []

    for region in regions:
        filtered_data_frame = df[df.region_x == region][['week_start', selected_metric]].groupby('week_start').agg('sum').reset_index()
        traces.append(go.Scatter(
            x = filtered_data_frame.week_start,
            y = filtered_data_frame[selected_metric],
            name = region
        ))

    return {'data': traces, 'layout': go.Layout()}


if __name__ == '__main__':
    app.run_server(debug=True)
