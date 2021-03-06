import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import dash_table
import dash_daq as daq
from dash.dependencies import Input, Output, State
import copy
from elasticsearch import Elasticsearch
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

es = Elasticsearch()

app = dash.Dash(__name__)

layout = dict(
    # autosize=True,
    # automargin=True,
    margin=dict(l=0, r=0, b=6, t=30),
    # hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    # width=350,
    # height=170,
    legend=dict(font=dict(size=10), orientation="v"),
    mapbox=dict(style="light",
                # center=dict(lon=-78.05, lat=42.54),
                zoom=2,
                ),
)

app.layout = html.Div(children=[
    dcc.Interval(
        id='interval',
        interval=5 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.H1(children='Malicious Domain Name Analysis',
            style={
                'textAlign': 'center',
                'color': '#2e86c1'
            }),
    html.Div(
        [
            html.Div(
                [
                    html.Div([
                        html.Div([
                            html.P(
                                "Domain Name:",
                                style={'display': 'inline', 'color': '#2e86c1',
                                       'font-size': '18px'},
                                className="control_label"
                            ),
                            dcc.Input(
                                placeholder='Enter a Domain Name',
                                type='text',
                                id='input_text',
                                className='dcc_control'
                            ),
                        ]),
                        html.Div(id='input_message', className="control_label"),
                        html.P("Enter the date range for the analysis:",
                               style={'color': '#2e86c1', 'font-size': '18px', },
                               className="control_label"),
                        dcc.DatePickerRange(
                            id='date_range',
                            min_date_allowed=dt(2020, 1, 5),
                            className="dcc_control",
                            style={'borderWidth': '0px', 'padding': '0px'},
                        ),
                        html.Div(id='date_message', className="control_label",
                                 style={'margin-bottom': '10px'}),
                        html.Div([
                            html.Div([
                                html.P("Requests per:",
                                       style={'display': 'inline',
                                              'color': '#2e86c1',
                                              'font-size': '18px'},
                                       className="control_label", ),
                                dcc.RadioItems(
                                    id="requests_freq",
                                    options=[
                                        {"label": "Day ", "value": "Day"},
                                        {"label": "Hour ", "value": "Hour"},
                                        {"label": "Minute ", "value": "Minute"},
                                    ],
                                    labelStyle={"display": "inline-block"},
                                    style={'color': '#2e86c1'},
                                    className="dcc_control",
                                ),
                            ]),
                            html.Div(id='radio_button_message',
                                     className="control_label",
                                     style={'margin-bottom': '10px'}),
                            html.Div([
                                html.P(
                                    "Hour Range:",
                                    style={'display': 'inline',
                                           'color': '#2e86c1',
                                           'font-size': '18px'},
                                    className="control_label"
                                ),
                                dcc.Input(
                                    placeholder='',
                                    type='text',
                                    id='start_hour',
                                    className='dcc_control',
                                    size='1'
                                ),
                                html.P(
                                    "to",
                                    style={'display': 'inline',
                                           'color': '#2e86c1',
                                           'font-size': '18px'},
                                    className="control_label"
                                ),
                                dcc.Input(
                                    placeholder='',
                                    type='text',
                                    id='end_hour',
                                    className='dcc_control',
                                    size='1'
                                ),

                            ], id='hour_range'),
                            html.Div(id='hour_range_message',
                                     className="control_label",
                                     style={'margin-bottom': '10px'}),
                            html.Div([html.P("Submit the Queries:",
                                             style={'display': 'inline',
                                                    'color': '#2e86c1',
                                                    'font-size': '18px'},
                                             className="control_label", ),
                                      html.Button('Submit',
                                                  id='submit_input',
                                                  n_clicks=0,
                                                  style={'float': 'center',
                                                         'margin-left': '30px',
                                                         'color': '#2e86c1'}, ),
                                      ], ),
                        ]),
                    ], className='pretty_container'),

                    html.Div([
                        dcc.Graph(id='pie_graph')
                    ], className="pretty_container",
                    )
                ],
                className="four columns",
                id="pie",
            ),
            html.Div([
                dcc.Tabs(id='tabs-example', value='tab-1', children=[
                    dcc.Tab([
                        html.Div([dcc.Graph(id='freq_graph', )]), ],
                        label='Requests Plot', value='tab-1',
                        className='pretty_container'),
                    dcc.Tab([
                        html.Div([
                            html.Br(),
                            html.P(
                                "List of IP addresses that queried the Domain",
                                style={'color': '#333',
                                       'font-size': '18px',
                                       'text-align': 'center'
                                       },
                                # className="control_label"
                            ),
                            html.Br(),
                            dash_table.DataTable(
                                id='ip_table_',
                                columns=[{'id': 'sl_no', 'name': 'Sl. No.'},
                                         {'id': 'ip', 'name': 'IP Address'},
                                         {'id': 'count', 'name': 'Queries'}],
                                fixed_rows={'headers': True},
                                style_table={
                                    'height': 380,
                                    'overflowY': 'auto',
                                    'backgroundColor': '#F9F9F9',
                                    'margin-left': '10px'
                                },
                                style_as_list_view=True,
                                style_cell={
                                    'padding': '5px',
                                    'backgroundColor': '#F9F9F9',
                                    'whiteSpace': 'no-wrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'textAlign': 'center',
                                    'font-family': 'Arial',
                                    'color': '#333',
                                    'fontSize': 15
                                },
                                style_header={
                                    'fontWeight': 'bold'
                                },
                            )
                        ], )
                    ], label='Queries per IP Address', value='tab-2',
                        className='pretty_container', id='ip_table'),
                    dcc.Tab([
                        daq.ToggleSwitch(
                            id='mal_toggle_switch',
                            value=False,
                            vertical=False,
                            labelPosition='bottom',
                            style={'float': 'right'}
                        ),
                        html.Br(),
                        html.Div([
                            html.Br(),
                            html.P(
                                "Malicious Domains",
                                style={'color': '#333',
                                       'font-size': '18px',
                                       'text-align': 'center'
                                       },
                                # className="control_label"
                            ),
                            html.Br(),
                            dash_table.DataTable(
                                id='mal_dns_table',
                                columns=[{'id': 'sl_no', 'name': 'Sl. No.'},
                                         {'id': 'domain',
                                          'name': 'Domain Names'},
                                         {'id': 'acc', 'name': 'Accuracy'},
                                         {'id': 'count', 'name': 'Queries'}],
                                fixed_rows={'headers': True},
                                data=[{'sl_no': 1, 'ip': 1, 'count': 1}],
                                style_table={
                                    'height': 360,
                                    'overflowY': 'auto',
                                    'backgroundColor': '#F9F9F9',
                                    'margin-left': '10px'
                                },
                                style_as_list_view=True,
                                style_cell={
                                    'padding': '5px',
                                    'backgroundColor': '#F9F9F9',
                                    'whiteSpace': 'no-wrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'textAlign': 'center',
                                    'font-family': 'Arial',
                                    'color': '#333',
                                    'fontSize': 15
                                },
                                style_header={
                                    'fontWeight': 'bold'
                                },
                            )
                        ], id='mal_dns_table_div'),
                        html.Div([
                            html.Br(),
                            dcc.Graph(id='mal_bar_graph', )],
                            id='mal_bar_graph_div'),
                    ],
                        label='Malicious Domains',
                        value='tab-3', className='pretty_container'),
                    dcc.Tab([
                        daq.ToggleSwitch(
                            id='benign_toggle_switch',
                            value=False,
                            vertical=False,
                            labelPosition='bottom',
                            style={'float': 'right'}
                        ),
                        html.Br(),
                        html.Div([
                            html.Br(),
                            html.P(
                                "Benign Domains",
                                style={'color': '#333',
                                       'font-size': '18px',
                                       'text-align': 'center'
                                       },
                                # className="control_label"
                            ),
                            html.Br(),
                            dash_table.DataTable(
                                id='benign_dns_table',
                                columns=[{'id': 'sl_no', 'name': 'Sl. No.'},
                                         {'id': 'domain',
                                          'name': 'Domain Names'},
                                         {'id': 'acc', 'name': 'Accuracy'},
                                         {'id': 'count', 'name': 'Queries'}],
                                fixed_rows={'headers': True},
                                style_table={
                                    'height': 360,
                                    'overflowY': 'auto',
                                    'backgroundColor': '#F9F9F9',
                                    'margin-left': '10px'
                                },
                                style_as_list_view=True,
                                style_cell={
                                    'padding': '5px',
                                    'backgroundColor': '#F9F9F9',
                                    'whiteSpace': 'no-wrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'textAlign': 'center',
                                    'font-family': 'Arial',
                                    'color': '#333',
                                    'fontSize': 15
                                },
                                style_header={
                                    'fontWeight': 'bold'
                                },
                            )
                        ], id='benign_dns_table_div'),

                        html.Div([
                            html.Br(),
                            dcc.Graph(id='benign_bar_graph', )],
                            id='benign_bar_graph_div'),

                    ],
                        label='Benign Domains',
                        value='tab-4', className='pretty_container'),

                ]),

            ], className="pretty_container eight columns",
                style={'color': '#2e86c1', 'font-size': '16px'}),

        ],
        className="row flex-display",
    ),
])


# Control Messages


@app.callback(Output('input_message', 'children'),
              [Input('submit_input', 'n_clicks')],
              [State('input_text', 'value')])
def input_message(n_clicks, value):
    if value is None or value == '':
        return 'Please enter a Domain Name'
    elif value in es.indices.get('*.com'):
        return 'You have entered: ' + value
    else:
        return 'Domain name does not exist in database'


@app.callback(Output('date_message', 'children'),
              [Input('submit_input', 'n_clicks'),
               Input('requests_freq', 'value'),
               Input('date_range', 'start_date'),
               Input('date_range', 'end_date')])
def date_message(n_clicks, freq, start_date, end_date):
    if start_date is None or end_date is None:
        return 'Please enter the date range'
    elif freq == 'Hour' or freq == 'Minute':
        start = int(start_date.split('-')[2])
        end = int(end_date.split('-')[2])
        if (end - start) == 1:
            return 'Data from {} to {}'.format(start_date, end_date)
        else:
            return 'For hours or minutes please enter two consecutive days'
    elif freq == 'Day':
        start = int(start_date.split('-')[1])
        end = int(end_date.split('-')[1])
        if (end - start) == 0:
            return 'Data from {} to {}'.format(start_date, end_date)
        else:
            return 'For days please enter a range within the same month'
    else:
        return 'Data from {} to {}'.format(start_date, end_date)


@app.callback(Output('radio_button_message', 'children'),
              [Input('submit_input', 'n_clicks'),
               Input('requests_freq', 'value')])
def radio_button_message(n_clicks, value):
    if value is None:
        return 'Please select an option'
    else:
        return 'You have selected: ' + value


@app.callback(Output('hour_range_message', 'children'),
              [Input('requests_freq', 'value'),
               Input('start_hour', 'value'),
               Input('end_hour', 'value')])
def hour_range_message(freq, start, end):
    if freq is None or freq == 'Day':
        return html.Div([])
    elif start is None or start is '' or end is None or end is '':
        return 'Enter an integer hour range (0 to 24)'
    else:
        try:
            start_ = int(start)
            end_ = int(end)
            diff = end_ - start_
            if 0 <= start_ <= 24 and 0 <= end_ <= 24 and diff > 0:
                if freq == 'Minute':
                    if diff > 1:
                        return 'The difference between the ranges should be 1'
                    else:
                        return 'Hour range from {} to {}'.format(start_, end_)
                else:
                    return 'Hour range from {} to {}'.format(start_, end_)
            else:
                return 'Please enter relevant integer values (0 to 24) '
        except:
            return 'Please enter integer values (0 to 24)'


# Graphs and Div Updates


@app.callback(Output('hour_range', 'style'),
              [Input('requests_freq', 'value')])
def display_hour_range(value):
    if value is None or value == 'Day':
        return {'display': 'none'}
    else:
        return {'display': 'unset'}


@app.callback(Output('pie_graph', 'figure'),
              [Input('submit_input', 'n_clicks')],
              [State('input_text', 'value')])
def update_pie_graph(n_clicks, value):
    layout_pie = copy.deepcopy(layout)
    layout_pie["title"] = 'Prediction'
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(font=dict(color="#777777", size="10"),
                                orientation="v", bgcolor="rgba(0,0,0,0)")
    layout_pie["width"] = '350'
    layout_pie["height"] = '150'
    if value is None or value is '':
        data = [
            dict(
                type="pie",
                labels=["Benign", "Malicious"],
                values=[0.5, 0.5],
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=["#3498db", "#f5b041 "]),
                domain={"x": [0.2, 0.9], "y": [0.2, 0.9]},
            )]
        figure = dict(data=data, layout=layout_pie)
        return figure
    else:
        try:
            pred = float(es.get(index=value, id=1)['_source']['status'])
        except:
            pred = 0.5
        data = [
            dict(
                type="pie",
                labels=["Benign", "Malicious"],
                values=[1 - pred, pred],
                textinfo="label+percent+name",
                hole=0.5,
                marker=dict(colors=["#3498db", "#f5b041 "]),
                domain={"x": [0.2, 0.9], "y": [0.2, 0.9]},
            )]
        figure = dict(data=data, layout=layout_pie)
        return figure


@app.callback(Output('freq_graph', 'figure'),
              [Input('submit_input', 'n_clicks'), ],
              [State('start_hour', 'value'),
               State('end_hour', 'value'),
               State('input_text', 'value'),
               State('date_range', 'start_date'),
               State('date_range', 'end_date'),
               State('requests_freq', 'value')])
def update_line_graph(n_clicks, start_hour, end_hour, input_value,
                      start_date, end_date, freq_value):
    layout_count = copy.deepcopy(layout)
    layout_count['title'] = "Requests"
    if freq_value is None:
        freq_value = ''
    layout_count['xaxis'] = {'title': 'Time in ' + freq_value + 's'}
    layout_count['yaxis'] = {'title': 'Number of Requests'}
    layout_count['autosize'] = True
    layout_count['margin'] = dict(l=0, r=0, b=20, t=30),
    if input_value is None or input_value == '' or start_date is None or \
            end_date is None or freq_value is None:
        layout_count['title'] = "Requests (Please fill the entries)"
        layout_count['xaxis'] = {'title': ''}
        data = [
            dict(
                type="line",
                # mode="markers",
                x=[],
                y=[],
                # opacity=0,
                hoverinfo="skip",
            )]
        figure = dict(data=data, layout=layout_count)
        return figure
    else:
        if freq_value == 'Minute':
            try:
                req = es.get(index=input_value, id=1)['_source'][start_date][start_hour]
                x = [i for i in req.keys()]
                y = [i for i in req.values()]
            except:
                layout_count['title'] = "Requests (Data not found)"
                layout_count['xaxis'] = {'title': ''}
                x = []
                y = []
            data = [
                dict(
                    type="line",
                    x=x,
                    y=y,
                )]
            figure = dict(data=data, layout=layout_count)
            return figure
        elif freq_value == 'Hour':
            try:
                req = es.get(index=input_value, id=1)['_source'][start_date]
                hours = [str(i) for i in range(int(start_hour), int(end_hour))]
                x = list(set(hours) & set(req.keys()))
                y = [np.sum(list(req[i].values())) for i in x]
            except:
                layout_count['title'] = "Requests (Data not found)"
                layout_count['xaxis'] = {'title': ''}
                x = []
                y = []
            data = [
                dict(
                    type="line",
                    x=x,
                    y=y,
                )]
            figure = dict(data=data, layout=layout_count)
            return figure
        elif freq_value == 'Day':
            start = start_date.split('-')
            start[1], start[2] = start[1].lstrip('0'), start[2].lstrip('0')
            end = end_date.split('-')
            end[1], end[2] = end[1].lstrip('0'), end[2].lstrip('0')

            try:
                req = es.get(index=input_value, id=1)['_source']
                req = req[start[0]][start[1]]
                print(req)
                if (int(end[1]) - int(start[1])) == 0:
                    days = [str(i) for i in range(int(start[2]),
                                                  (int(end[2]) + 1))]

                    x = list(set(days) & set(req.keys()))
                    y = [req[i] for i in x]
                else:
                    x = [i for i in req.keys()]
                    y = [req[i] for i in x]
            except:
                layout_count['title'] = "Requests (Data not found)"
                layout_count['xaxis'] = {'title': ''}
                x = []
                y = []
            data = [
                dict(
                    type="line",
                    x=x,
                    y=y,
                )]
            figure = dict(data=data, layout=layout_count)
            return figure


@app.callback(Output('ip_table_', 'data'),
              [Input('submit_input', 'n_clicks')],
              [State('input_text', 'value')])
def update_ip_table(nclicks, value):
    if value is None or value == '':
        return []
    else:
        try:
            count = es.get(index=value, id=1)['_source']['count']
            domain_names = [key for (key, value) in sorted(count.items(),
                                                           key=lambda x: x[1],
                                                           reverse=True)]
            data = [dict({'sl_no': j + 1, 'ip': i, 'count': count[i]})
                    for i, j in zip(domain_names, range(len(count)))]
        except:
            data = []
        return data


@app.callback(Output('mal_dns_table_div', 'style'),
              [Input('mal_toggle_switch', 'value')])
def display_mal_list(value):
    if value is False:
        return {'display': 'none'}
    else:
        return {'display': 'unset'}


@app.callback(Output('mal_bar_graph_div', 'style'),
              [Input('mal_toggle_switch', 'value')])
def display_mal_graph(value):
    if value is False:
        return {'display': 'unset'}
    else:
        return {'display': 'none'}


@app.callback(Output('mal_dns_table', 'data'),
              [Input('mal_toggle_switch', 'value'),
               Input('interval', 'n_intervals')])
def update_mal_dns_table(nclicks, value):
    try:
        count = es.get(index='mal', id=1)['_source']
        domain_names = [key for (key, value) in sorted(count.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)]
        data = [dict({'sl_no': j + 1, 'domain': i, 'count': count[i]})
                for i, j in zip(domain_names, range(len(count)))]
    except:
        data = []
    return data


@app.callback(Output('mal_bar_graph', 'figure'),
              [Input('mal_toggle_switch', 'value'),
               Input('interval', 'n_intervals')])
def update_mal_bar_graph(value, interval):
    try:
        mal = es.get(index='mal', id=1)['_source']
    except:
        mal = {}
    if len(mal) < 20:
        domain_names = [key for (key, value) in sorted(mal.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)]
    else:
        domain_names = [key for (key, value) in sorted(mal.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)][0:20]

    layout_bar = copy.deepcopy(layout)
    layout_bar['title'] = "Top Malicious Domains Queried"
    layout_bar['xaxis'] = {'title': 'Rank (Hover over the bars for more info)',
                           'tickvals': [(i + 1) for i in
                                        range(len(domain_names))]}
    layout_bar['yaxis'] = {'title': 'Number of Requests'}
    layout_bar['margin'] = dict(l=30, r=30, b=20, t=30),
    layout_bar['height'] = '400'
    data = [
        dict(
            type="bar",
            hovertext=domain_names,
            x=[(i + 1) for i in range(len(domain_names))],
            y=[int(mal[i]) for i in domain_names],
        )]
    figure = dict(data=data, layout=layout_bar)
    return figure


@app.callback(Output('benign_dns_table_div', 'style'),
              [Input('benign_toggle_switch', 'value')])
def display_benign_list(value):
    if value is False:
        return {'display': 'none'}
    else:
        return {'display': 'unset'}


@app.callback(Output('benign_bar_graph_div', 'style'),
              [Input('benign_toggle_switch', 'value')])
def display_benign_graph(value):
    if value is True:
        return {'display': 'none'}
    else:
        return {'display': 'unset'}


@app.callback(Output('benign_dns_table', 'data'),
              [Input('mal_toggle_switch', 'value'),
               Input('interval', 'n_intervals')])
def update_benign_dns_table(nclicks, value):
    try:
        count = es.get(index='benign', id=1)['_source']
        domain_names = [key for (key, value) in sorted(count.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)]
        data = [dict({'sl_no': j + 1, 'domain': i, 'count': count[i]})
                for i, j in zip(domain_names, range(len(count)))]
    except:
        data = []
    return data


@app.callback(Output('benign_bar_graph', 'figure'),
              [Input('benign_toggle_switch', 'value'),
               Input('interval', 'n_intervals')])
def update_benign_bar_graph(value, interval):
    try:
        benign = es.get(index='benign', id=1)['_source']
    except:
        benign = {}
    if len(benign) < 20:
        domain_names = [key for (key, value) in sorted(benign.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)]
    else:
        domain_names = [key for (key, value) in sorted(benign.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)][0:20]

    layout_bar = copy.deepcopy(layout)
    layout_bar['title'] = "Top Benign Domains Queried"
    layout_bar['xaxis'] = {'title': 'Rank (Hover over the bars for more info)',
                           'tickvals': [(i + 1) for i in
                                        range(len(domain_names))]}
    layout_bar['yaxis'] = {'title': 'Number of Requests'}
    layout_bar['margin'] = dict(l=30, r=30, b=20, t=30),
    layout_bar['height'] = '400'
    data = [
        dict(
            type="bar",
            hovertext=domain_names,
            x=[(i + 1) for i in range(len(domain_names))],
            y=[int(benign[i]) for i in domain_names],
        )]
    figure = dict(data=data, layout=layout_bar)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
