################################################################################
###
### Libraries
###
################################################################################
import dash
from dash import dcc, html, dash_table
from dash import html
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc

import base64
import json
import webbrowser
import io
import pandas as pd

################################################################################
###
### Setup
###
################################################################################
app = dash.Dash(__name__, external_stylesheets=['bootstrap.css', 'criddyp.css', 'custom.css'], title='Data Monger', update_title=None, prevent_initial_callbacks=True)
app.config.suppress_callback_exceptions = True

# Globals
global data_1
global data_2
global data_merged

################################################################################
###
### Layout
###
################################################################################
app.layout =  html.Div([

    # Add in title
    dbc.Row(
        [
            html.P('Data Monger 3000', className='title'),
        ],
    ),

    dbc.Row(
        [
            # Data file 1 preview
            html.Div(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H4('Dataset 1', className='heading'),
                                    dcc.Upload(
                                        id='upload-data-1',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select File')
                                        ]),
                                        className='b_upload',
                                        multiple=False,
                                    ),
                                ],
                            ),
                            dbc.CardBody(dbc.Spinner(html.Div(id='upload_data_1_preview',className='data_table_preview'), color="primary", spinner_style={"width": "3rem", "height": "3rem"})),
                            dbc.CardFooter(
                                html.Div(id='data_1_stats', className='card_footer_stats')
                            ),
                        ],
                        className='card_data_table',
                    ),
                ], 
                style={'width': '50%',  'display': 'inline-block'},              
            ),

            # Data file 2 preview
            html.Div(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H4('Dataset 2', className='heading'),
                                    dcc.Upload(
                                        id='upload-data-2',
                                        children=html.Div([
                                            'Drag and Drop or ',
                                            html.A('Select File')
                                        ]),
                                        className='b_upload',
                                        multiple=False,
                                    ),
                                ],
                            ),
                            dbc.CardBody(dbc.Spinner(html.Div(id='upload_data_2_preview',className='data_table_preview'), color="primary", spinner_style={"width": "3rem", "height": "3rem"})),
                            dbc.CardFooter(
                                html.Div(id='data_2_stats', className='card_footer_stats')
                            ),
                        ],
                        className='card_data_table',
                    ),
                ], 
                style={'width': '50%',  'display': 'inline-block'},              
            ),
        ],
    ),

    # options for joins and cols
    dbc.Row(
        [
            # Join Type
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H4('Type of Transformation', className='heading'),),
                        dbc.CardBody(
                            [
                                dbc.RadioItems(
                                options=[
                                    {"label": "Union", "value": 'Union'},
                                    {"label": "Inner", "value": 'Inner'},
                                    {"label": "Outer", "value": 'Outer'},
                                    {"label": "Left", "value": 'Left'},
                                    {"label": "Right", "value": 'Right'},
                                    {"label": "Cross", "value": 'Cross'},
                                    ],
                                value='Union',
                                className='join-list',
                                id='join_select',
                                ),
                            ],
                        ),
                    ],
                    className='card_transform_type',
                ),
            ),

            dbc.Col(
                # Cols to join/union on 
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4('Col Logic', className='heading'),
                                dbc.Button("Add Join Col", id="b_add_col_match",n_clicks=0, className='b_add_col'),
                                dbc.Button("Refresh", id="b_refresh_col_match",n_clicks=0, className='b_add_col'),
                            ],
                        ),
                        dbc.CardBody(
                            [
                                html.Div(id="col_match_input", children=[]),
                            ],
                            className='col_match_container',
                        ),
                    ],
                    className='card_col_logic',
                ),
            ),
        ],
    ),

    # Submit button
    dbc.Row(
        dbc.Button('Run Join/Union', id="b_run_joins",n_clicks=0, className='b_submit'),
    ),

    # Data preview for merged data
    dbc.Row(
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H4('Output Dataset', className='heading'),
                        # html.Button('Run Join/Union', id="b_run_joins",n_clicks=0, className='b_join'),
                        html.Button('Download', id="b_download",n_clicks=0, className='b_download', style={'display':'none'}),
                        dcc.Download(id="download-dataframe-csv")

                    ],
                ),

                dbc.CardBody(
                    [
                        dbc.Spinner(html.Div(id='agg_data_preview', className='data_table_preview_merged'), color="primary", spinner_style={"width": "3rem", "height": "3rem"}),
                    ],
                ),
                dbc.CardFooter(
                    html.Div(id='data_merged_stats', className='card_footer_stats')
                ),
            ],
            className='card_data_table_merged'
        ),
    ),
],)

################################################################################
###
### Callbacks
###
################################################################################
# Content parse for csv and excel files
# https://dash.plotly.com/dash-core-components/upload
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df

# parse data stats
def parse_stats(df):
    # fill blank cells with 0
    df = df.fillna(0)
    children = []

    # add num rows and cols
    children.append(html.P('Rows: ' + "{:,}".format(df.shape[0])))
    children.append(html.P('Cols: ' + "{:,}".format(df.shape[1])))
    
    # iterate col names and data
    for (name, data) in df.iteritems():
        try:
            # Calculate col sum and format with ,'s
            temp_sum = sum(data.values)
            temp = name + ': ' + "{:,}".format(temp_sum)
            # only show data greater than 0
            if temp_sum > 0:
                children.append(html.P(temp))
            else:
                # ignore data summed as 0
                # This will prevent empty cols populated with 0 from showing up and taking up space
                pass
                
        except:
            # unable to sum values (strings or non int type)
            pass
    return children

# upload data 1/ preview
@app.callback(
    [
        Output('upload_data_1_preview', 'children'),
        Output('data_1_stats', 'children'),
    ],
    Input('upload-data-1', 'contents'),
    State('upload-data-1', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        # Declare global
        global data_1
        # Parse contents
        try:
            data_1 = parse_contents(contents, filename)
        except:
            return 'Unable to parse file', ''

        # Return data table and parsed df stats
        return dash_table.DataTable(
				columns=[{"name": i, "id": i} for i in data_1.columns],
				data=data_1.to_dict("rows"),
                # fixed_rows={'headers': True, 'data': 0},
				style_cell={'color': 'black',
				'textAlign': 'left',},
                ), parse_stats(data_1)

# upload data 2/ preview
@app.callback(
    [
        Output('upload_data_2_preview', 'children'),
        Output('data_2_stats', 'children'),
    ],
    Input('upload-data-2', 'contents'),
    State('upload-data-2', 'filename')
)
def update_output(contents, filename):
    if contents is not None:
        # Declare global
        global data_2
        # Parse contents
        try:
            data_2 = parse_contents(contents, filename)
        except:
            return 'Unable to parse file', ''

        return dash_table.DataTable(
				columns=[{"name": i, "id": i} for i in data_2.columns],
				data=data_2.to_dict("rows"),
                # fixed_rows={'headers': True, 'data': 0},
				style_cell={'color': 'black',
				'textAlign': 'left',},
                ), parse_stats(data_2)

# Display dropdowns
@app.callback(
    Output('col_match_input', 'children'),
    [
        Input('b_add_col_match', 'n_clicks'),
        Input('b_refresh_col_match', 'n_clicks'),
        Input({'type': 'b_del_col', 'index': ALL}, 'n_clicks'),
    ],
    [
        State('col_match_input', 'children'),
        State({"index": ALL, "type": "dropdown_col_1"}, "value"),
        State({"index": ALL, "type": "dropdown_col_2"}, "value"),
    ],
    prevent_initial_call=True)
def display_dropdowns(b_add_n_clicks, b_refresh_n_clicks, b_del_n_clicks, children, col1, col2):
    # Find which element triggered the callback (add or del)
    triggered = [p['prop_id'].split('.')[0] for p in dash.callback_context.triggered]
    if triggered == 'upload-data-1':
        pass
    
    # declare globals
    global data_1
    global data_2

    # Test if globals have any data assigned to them
    try:
        data_1.columns
        data_2.columns
    except:
        # If there are no loaded datasets then return an empty list
        return ['']

    # make sure to remove any blank elements that could have been loaded from the above try
    try:
        children.remove('')
    except:
        pass

    # generate our new list out of current elements
    new_spec = [
        (children, col1, col2) for children, col1, col2 in zip(children, col1, col2)
    ]

    # if we are deleting an element
    try:
        if 'b_del_col' in json.loads(triggered[0])['type']:
            del new_spec[(json.loads(triggered[0])['index'])]
    except:
        pass

    # if we are adding append the added item to our list of elements
    if 'b_add_col_match' in triggered:
        new_spec.append(('','', []))
    
    ## Re-index
    # iterate through all elements to create a new list of elements
    # the reason the whole list is re-created every time rather than using
    # a flat list is to better keep track of the list index for removing items.
    new_element = [
        html.Div([
            dcc.Dropdown(
                options=data_1.columns,
                value = col1,
                id={
                    'type': 'dropdown_col_1',
                    'index': i
                },
                className='col_dropdown',
            ),
            dcc.Dropdown(
                options=data_2.columns,
                value = col2,
                id={
                    'type': 'dropdown_col_2',
                    'index': i
                },
                className='col_dropdown',
            ),
            html.Button('Del',id={
                    'type': 'b_del_col',
                    'index': i
                    }, 
                className='b_del_col')
        ])
    for i, (children, col1, col2) in enumerate(new_spec)
    ]

    return new_element

# Merge data and preview
@app.callback(
    [
    Output(component_id='agg_data_preview', component_property='children'),
    Output(component_id='b_download', component_property='style'),
    Output('data_merged_stats', 'children')
    ],
    Input(component_id='b_run_joins', component_property='n_clicks'),
    [
        State(component_id='join_select', component_property='value'),
        State(component_id={'type': 'dropdown_col_1', 'index': ALL}, component_property='value'),
        State(component_id={'type': 'dropdown_col_2', 'index': ALL}, component_property='value'),
    ],
)
def merge_data(n, join_type, dropdown_1, dropdown_2):
    triggered = [p['prop_id'].split('.')[0] for p in dash.callback_context.triggered]
    
    # make sure correct trigger
    if 'b_run_joins' in triggered:
        # declare globals
        global data_1
        global data_2
        global data_merged
        try:
            data_1.columns
            data_2.columns
        except:
            # If there are no loaded datasets then return an eror
            return html.P('Please make sure data is uploaded'), {'display': 'none'}, ''
        join_type = join_type.lower()
        
        # check if join type is union (only one with different context)
        if join_type == 'union':
            data_merged = pd.concat([data_1, data_2])
            return dash_table.DataTable(
				columns=[{"name": i, "id": i} for i in data_merged.columns],
				data=data_merged.to_dict("rows"),
                # fixed_rows={'headers': True, 'data': 0},
				style_cell={'color': 'black',
				'textAlign': 'left',},
                ), {'display': 'block'}, parse_stats(data_merged)

        # special rules for cross join
        elif join_type =='cross':
            data_merged = pd.merge(data_1, data_2, how = join_type)
            return dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in data_merged.columns],
                data=data_merged.to_dict("rows"),
                # fixed_rows={'headers': True, 'data': 0},
                style_cell={'color': 'black',
                'textAlign': 'left',},
                ), {'display': 'block'}, parse_stats(data_merged)

        # for a regular join type
        else:
            # make sure there are cols selected for join
            if dropdown_1 == [] or dropdown_2 == []:
                return html.P('Select some cols to join on'), {'display': 'none'}, ''
            if None in dropdown_1 or None in dropdown_2:
                return html.P('Please make sure all cols joins are filled out'), {'display': 'none'}, ''

            # if cols for join are selected
            else:
                data_merged = pd.merge(data_1, data_2, left_on=dropdown_1,
                   right_on=dropdown_2, 
                   how = join_type)
                return dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in data_merged.columns],
                    data=data_merged.to_dict("rows"),
                    # fixed_rows={'headers': True, 'data': 0},
                    style_cell={'color': 'black',
                    'textAlign': 'left',},
                    ), {'display': 'block'}, parse_stats(data_merged)

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("b_download", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    triggered = [p['prop_id'].split('.')[0] for p in dash.callback_context.triggered]
    
    # make sure correct trigger
    if 'b_download' in triggered:
        global data_merged
        return dcc.send_data_frame(data_merged.to_csv, filename='merged.csv', index=False)

    # Row and col count

################################################################################
###
### Run
###
################################################################################
if __name__ == '__main__':
    webbrowser.open('http://localhost:8080/')
    app.run_server(debug=False, port=8080, host='localhost')
