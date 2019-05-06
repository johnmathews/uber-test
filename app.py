# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import timedelta as td
from datetime import datetime
import pandas as pd
import numpy as np

region = 'EMEA - NEE'
metric = 'sessions'
date = '2019/04/01'

df = pd.read_csv('uber-data.csv', infer_datetime_format=True, parse_dates=[0])
df.week_start = pd.to_datetime(df.week_start, infer_datetime_format=True)
df = df.sort_values(by='week_start', ascending=True)

available_regions = df.region_x.unique()
available_dates = [np.datetime64(x, 'D') for x in  df.week_start.unique()]

def total_of_metric(region, metric, week):
    return df[(df.week_start == week) & (df.region_x == region)][[metric]].sum()

def metric_change_week_on_week(region, metric, week):
    current_week = datetime.strptime(week, '%Y/%m/%d')
    previous_week = current_week - td(days=7)

    weekly_total = df[(df.week_start == current_week) & (df.region_x == region)][[metric]].sum()
    previous_weekly_total = df[(df.week_start == previous_week) & (df.region_x == region)][[metric]].sum()

    change = (weekly_total - previous_weekly_total) / previous_weekly_total
    return change

total_of_metric(region, metric, date)
metric_change_week_on_week(region, metric, date)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
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
    'margin': 5,
    'width': sub_total_width,
    'margin-left': 'auto',
    'backgroundColor': colors['background'],
    'color': colors['text'],
    'textAlign': 'center'
}


app.layout = html.Div([

    html.Div([
        html.Div(
            dcc.Dropdown(
                id='region_dropdown',
                options=[{'label': i, 'value': i} for i in available_regions],
                value=available_regions[0]
            ),
            style=dropdown_style
        ),
        html.Div(
            dcc.Dropdown(
                id='dates_dropdown',
                options=[{'label': i, 'value': i} for i in available_dates],
                value=available_dates[-1]
            ),
            style=dropdown_style
        ),
    ]),

    html.Div([
        html.Div(
            children='EMEA',
            style=region_heading_style
        ),
        html.Div(
            children='MEA',
            style=region_heading_style
        ),
        html.Div(
            children='WSE',
            style=region_heading_style
        ),
        html.Div(
            children='NEE',
            style=region_heading_style
        ),
    ]),
    html.Div([
        html.Div(
            children='EMEA',
            style=total_style_dict
        ),
        html.Div(
            children='MEA',
            style=total_style_dict
        ),
        html.Div(
            children='WSE',
            style=total_style_dict
        ),
        html.Div(
            children='NEE',
            style=total_style_dict
        ),
        html.Div(
            children='EMEA',
            style=total_style_dict
        ),
        html.Div(
            children='MEA',
            style=total_style_dict
        ),
        html.Div(
            children='WSE',
            style=total_style_dict
        ),
        html.Div(
            children='NEE',
            style=total_style_dict
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
