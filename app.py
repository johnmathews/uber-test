# -*- coding: utf-8 -*-
from datetime import datetime, timedelta as td
import numpy as np
import pandas as pd

import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

# Load extra layouts
cyto.load_extra_layouts()

# import data
df = pd.read_csv('uber-data.csv', infer_datetime_format=True, parse_dates=[0])
df.week_start = pd.to_datetime(df.week_start, infer_datetime_format=True)
df = df.sort_values(by='week_start', ascending=True)

available_metrics = df.columns[5:]
available_dates = [np.datetime64(x, 'D') for x in df.week_start.unique()]
available_regions = df[df.region_x != 'EMEA'].region_x.unique()


# reusable components
region_names = ['EMEA', 'MEA', 'WSE', 'NEE']
region_names_long = ['EMEA', 'EMEA - MEA', 'EMEA - WSE', 'EMEA - NEE']
metric_names = ['_change', '_total']
metrics_for_each_region = [x+i for x in region_names for i in metric_names]


# calculate weekly total
def total_of_metric(region, metric, week):
    if region == 'EMEA':
        result = df[df.week_start == week][[metric]].sum().item()
    else:
        result = df[(df.week_start == week) & (df.region_x == region)][[metric]].sum().item()
    return f"total: {result:,}"


# calculate week on week change
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


# generate callbacks for each region
def responsive_metrics(name):
    if name != 'EMEA':
        long_name = f'EMEA - {name}'
    else:
        long_name = name

    @app.callback(
        Output(component_id=f'{name}_total', component_property='children'),
        [Input(component_id='dates_dropdown', component_property='value'),
         Input(component_id='metrics_dropdown', component_property='value')])
    def update_output_div(dates_dropdown, metrics_dropdown):
        return total_of_metric(long_name, metrics_dropdown, dates_dropdown)

    @app.callback(
        Output(component_id=f'{name}_change', component_property='children'),
        [Input(component_id='dates_dropdown', component_property='value'),
         Input(component_id='metrics_dropdown', component_property='value')])
    def update_output_div(dates_dropdown, metrics_dropdown):
        return metric_change_week_on_week(long_name, metrics_dropdown, dates_dropdown)


app = dash.Dash(__name__,  meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

# styling
default_style = {
    'margin': 5,
    'padding': 5,
    'display': 'flex',
    'flex-direction': 'row',
    'backgroundColor': '#111111',
    'color': '#FFFFFF',
    'textAlign': 'center',
    'borderRadius': 3,
    'width': '12.5%',
}

region_heading_style = default_style.copy()
region_heading_style['width'] = '25%'

metrics_style = default_style.copy()
metrics_style['width'] = '12.5%'

drilldown_title = default_style.copy()
drilldown_title['width'] = '85%'
drilldown_title['flex-direction'] = 'column'

drilldown_abs_change = default_style.copy()
drilldown_abs_change['width'] = '40%'
drilldown_abs_change['flex-direction'] = 'row'

drilldown_rel_change = default_style.copy()
drilldown_rel_change['width'] = '40%'
drilldown_rel_change['flex-direction'] = 'row'

dropdown_style = {
    'margin-left': '2%',
    'margin-right': '2%',
    'position': 'relative',
    'align': 'center',
    'display': 'inline',
}

node_style = dropdown_style.copy()
node_style['width'] = '25%'
node_style['align'] = 'left'

metric_components = {
    'trips_completed': ['requests', 'driver_cancelled', 'rider_cancelled'],
    'requests': ['sessions', 'surged_trips']
}

#  def metric_drill_down(metric='trips_completed'):
#      result = [drill_down_unit(title=metric)]
#      components = [drill_down_unit(title=component) for component in metric_components[metric]]
#      #  hidden_components = [drill_down_unit(title=component, hidden=True) for component in metric_components[metric]]
#      result =  result + components
#      return result
#
#  #  [html.Div(id=metric, children='start', style=metrics_style) for metric in metrics_for_each_region]
#  def drill_down_unit(title='title', abs_change='abs_change', rel_change='rel_change', hidden=False):
#      return html.Div([
#          html.Div([
#              title
#              ], style=drilldown_title),
#          html.Div([
#              html.Div([
#                  abs_change
#              ], style=drilldown_abs_change),
#              html.Div([
#                  rel_change
#              ], style=drilldown_rel_change)
#          ], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'}),
#      ], id=f'id_{title}', style={'display': 'flex', 'flexDirection': 'column', 'width': '20%'})

node_directions = {
    'completed_trips': ['requests', 'driver cancel', 'rider cancel', 'unfulfilled trips'],
    'requests': ['sessions', 'surged trips'],
    'surged trips': ['apple', 'banana'],
    'driver cancel': [],
    'rider cancel': [],
    'unfulfilled trips': [],
    'sessions': [],
}

nodes = [
    {
        'data': {'id': id, 'label': label},
    }
    for id, label in (
        ('completed trips', 'completed trips'),
        ('requests', 'requests'),
        ('driver cancel', 'driver cancel'),
        ('rider cancel', 'rider cancel'),
        ('sessions', 'sessions'),
        ('surged trips', 'surged trips'),
        ('apple', 'apple'),
        ('banana', 'banana')
    )
]

edges = [
    {'data': {'source': source, 'target': target}}
    for source, target in (
        ('completed trips', 'requests'),
        ('completed trips', 'driver cancel'),
        ('completed trips', 'rider cancel'),
        ('requests', 'sessions'),
        ('requests', 'surged trips'),
        ('surged trips', 'apple'),
        ('surged trips', 'banana'),
    )
]


# page structure - uses flexbox for responsive design
app.layout = html.Div([

    # menues to select metric and week
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
    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '12.5%', 'margin-left': 'auto'}),

    # region titles
    html.Div(
        [html.Div(children=region, style=region_heading_style) for region in region_names]
    , style={'display': 'flex', 'flexDirection': 'row'}),

    # region metrics; total, change
    html.Div(
        [html.Div(id=metric, children='start', style=metrics_style) for metric in metrics_for_each_region]
    , style={'display': 'flex', 'flexDirection': 'row'}),

    # line charts
    html.Div([
        html.Div([
            dcc.Graph(id="regions", config={'displayModeBar': False}),
            ]),
        html.Div([
            dcc.Graph(id="sub-regions", config={'displayModeBar': False}),
            ])
    ], style={'display': 'flex', 'flexDirection': 'row'}),

    # drill down element
    html.Div(
        dcc.Dropdown(
            id='node_dropdown',
            options=[{'label': i, 'value': i} for i in node_directions.keys()],
            value=list(node_directions.keys())[0],
            clearable=False,
        ),
        style={'width': '200px'}
    ),
    html.Div([
        cyto.Cytoscape(
            id='metric_explorer',
            layout={'name': 'breadthfirst', #dagre
                    'fit': 'true',
                    'maximal': 'false',
                    'directed': 'true',
                   },
            style={'width': '70%', 'height': '400px'},
            elements=nodes+edges,
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {'label': 'data(label)',
                    "text-wrap": "wrap",
                    'font-size': 22,
                             }}
            ],
                )
    ])
    #  html.Div([
    #      dcc.Store(id='memory'),
    #      html.Div(id='metric_explorer', children = metric_drill_down()
    #      ,  style={'display': 'flex', 'flexDirection': 'row', 'width': '75%'}),
    #
    #  ], style={'display': 'flex', 'flexDirection': 'column'})
    ])

# callbacks for weekly region totals and change, must come after `app.layout` has been defined
for region in region_names:
    responsive_metrics(region)


@app.callback(
    Output('metric_explorer', 'elements'),
    [Input('dates_dropdown', 'value'),
     Input('metric_explorer', 'tapNodeData')]
)
def update_elements(dates_dropdown, tapNodeData):
    current_week = datetime.strptime(dates_dropdown, '%Y-%m-%d')
    print(f'node: {tapNodeData}')
    def get_abs_change(date, metric):
        previous_week = current_week - td(days=7)
        weekly_total = df[df.week_start == current_week][[node_dropdown]].sum().item()
        previous_weekly_total = df[df.week_start == previous_week][[node_dropdown]].sum().item()
        change = 100 * ((weekly_total - previous_weekly_total) / previous_weekly_total)
        string = f' \nabs: {round(weekly_total,0)} change: {round(change,2)}%'
        return string

    node_list = [node_dropdown] + node_directions[node_dropdown]
    for node in node_directions[node_dropdown]:
        node_list = node_list + node_directions[node]
    nodes = (
        {
            'data': {'id': id, 'label': label},
        }
        for id, label in ([(i,i+get_abs_change(dates_dropdown, i)) for i in node_list])
    )
    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in (
        (parent, child) for parent in node_directions for child in node_directions[parent]
        )
    ]
    elements = list(nodes) + list(edges)
    return elements


#  # callbacks for drill down
#  @app.callback(
#      Output(component_id='metric_explorer', component_property='children'),
#      [(Input(component_id=f'id_{each_metric}', component_property='children')) for each_metric in metric_components]
#  )
#  def drill_down(selected_metric):
#      return metric_drill_down(selected_metric)

# callbacks for line charts
@app.callback(
    Output(component_id='regions', component_property='figure'),
    [Input(component_id='metrics_dropdown', component_property='value')]
)
def update_figure(selected_metric):
    regions = df[df.region_x != 'EMEA'].region_x.unique()
    traces = []

    for region in regions:
        filtered_data_frame = df[df.region_x == region]\
                [['week_start', selected_metric]].groupby('week_start').agg('sum').reset_index()
        traces.append(go.Scatter(
            x=filtered_data_frame.week_start,
            y=filtered_data_frame[selected_metric],
            name=region[6:]
        ))

    return {'data': traces,
            'layout': go.Layout(title=selected_metric.replace('_', ' ').title(),
                                autosize=True,
                                hovermode='closest',
                                legend={'orientation': 'h'},
                                )
            }


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
        filtered_data_frame = df[df.sub_region_x == sub_region]\
                [['week_start', selected_metric]].groupby('week_start').agg('sum').reset_index()
        traces.append(go.Scatter(
            x=filtered_data_frame.week_start,
            y=filtered_data_frame[selected_metric],
            name=sub_region
        ))

    return {'data': traces,
            'layout': go.Layout(title=region[6:] + f': {selected_metric}'.replace('_', ' '),
                                autosize=True,
                                legend={'orientation': 'h'}
                                )
            }


if __name__ == '__main__':
    app.run_server(debug=False)
