import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.io as pio
from dash.dependencies import Input, Output, State
import pandas as pd
import random
from datetime import datetime
from src.data import DataLoader
from src.ml import load_and_predict_model, data_preprocessing


app = dash.Dash(__name__)
pio.templates.default = "plotly_dark"

# Style constants
color_map = {
    "S": "red",
    "M": "blue",
    "L": "blue",
    "MP": "green",
    "C": "green",
    "SD": "yellow",
    "V": "red",
    "Uncertain": "gray",
    "FI": "pink",
    "KD": "purple"
}

support_labels = {
    "publdate": "Publishing Date",
    "support": "Support",
    "party": "Party",
    "likeness": "Similarity (%)"
}

# Instatiate DataLoader
DataLoader = DataLoader()

# Load hashtag data
hashtags = DataLoader.load_hashtags()

# Load party poll numbers
polls = DataLoader.load_party_poll_numbers()

# Begin app layout
app.layout = html.Div(children=[
    html.H1(children='Analysis of #svpol: Explore the World of Swedish Political Twitter'),

    # Empty spacer
    html.Div([]),

    # Machine Learning part of the app
    html.Div([
        html.H3(children="Predict political leanings in Swedish text"),
        html.Div(children="""
            This graph below is powered by a machine learning model. A gradient boosted tree to be specific. The model was trained on 
            tweets from political Swedish twitter accounts, as well as the respective party website of each Swedish parliamentary party.
            Paste some Swedish text into the text field and hit "Predict" to get a similarity score for the political leaning of your text.
            Note: the model is still under refinement - don't expect miracles yet :) 
        """, style={'width': '45%', 'display': 'inline-block', "padding-right": "2%"}),
        html.Div([
            dcc.RadioItems(id="ml_radio",
            options=[
                #{"label": "Twitter handle", "value": "twitter_handle"},
                {"label": "Free text", "value": "free_text"} 
            ],
            value="free_text"
            ),
            html.Div(
                dcc.Textarea(id="input-on-submit", 
                placeholder="Paste your text here and press Predict", 
                style={"width": "100%", "heigth": "100%", "rows": 5, "resize": "none"})
            ),
                html.Button('Predict', id='submit-val', n_clicks=0)
            ], style={'width': '45%', 'display': 'inline-block'})
        ]),
    # Div that holds the ML outputs - bar chart
    html.Div([
        dcc.Graph(id="ml_prediction_bargraph")
    ], style={"padding-top": "2%"}),

    # Statistical part of the app
    html.Div([
        html.H3(children="Hashtag mentions over time"),
        html.Div(children="""
            Select a hashtag from the dropdown menu to see its usage over time together with
            the main Swedish political twitter hashtag #svpol.
        """, style={"bottom-padding": "2%"}),
    ]),
    html.Div([
        html.Div([
            dcc.Dropdown(
            id="dropdown_hashtag",
            options=[{"label": x, "value": x} 
                    for x in DataLoader.get_list_of_trending_hashtags()],
            value="#svpol",
            clearable=False,
        )], style = {"width": "33%", "color": "black", "display": "inline-block"}),
        html.Div([
            dcc.Slider(
                id="slider_hashtag_horizon",
                min=1,
                max=30,
                step=1,
                value=5,
            )], style = {
                    "width": "33%", 
                    "display": "inline-block", 
                    "-ms-transform": "translateY(+50%)",
                    "transform": "translateY(+50%)"
                    }
                ),
        html.Div(id="slider_label", 
                style={
                    "width": "33%", 
                    "display": "inline-block", 
                    "color": "red","-ms-transform": "translateY(-50%)",
                    "transform": "translateY(-50%)"}
                    ),
    ]),
    
    dcc.Graph(id="timeseries"),

    html.Div([
        html.H3(children="Party support from polling institutes"),
        html.Div([
            dcc.Dropdown(
                id="dropdown_polling_company",
                options=[{"label": x, "value": x}
                    for x in polls.company.unique().tolist()],
                value="Sifo",
                clearable=False,
                style = {"color": "black"},
            ),
        ],style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id="dropdown_polling_date",
                clearable=False,
                style = {"color": "black"},
            )
        ],style={'width': '33%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(
        id="party_bar"
    ),

    html.Div([
        html.H3(children="Party support over time from polling institutes"),
        html.Div([
            dcc.Dropdown(
                id="dropdown_polling_company_timeseries",
                options=[{"label": x, "value": x}
                    for x in polls.company.unique().tolist()],
                value="Sifo",
                clearable=False,
                style = {"color": "black"}
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            dcc.RangeSlider(
                id="polling_year_rangeslider",
                min=2000,
                max=2021,
                step=None,
                marks={i: str(i) for i in range(2000, 2022)},
                value=[2000, 2021]
            )
        ], style={'width': '66%', 'display': 'inline-block', "color": "white"}),

        dcc.Graph(
            id="party_lines"
        )
    ])
])

# Callbacks
@app.callback(
    Output("party_lines", "figure"),
    [Input("dropdown_polling_company_timeseries", "value"),
    Input("polling_year_rangeslider", "value")]
)
def display_party_lines_timeseries(polling_company, year_range):
    # Figure for party support over times
    party_lines_df = DataLoader.load_party_poll_numbers(publ_year_start=year_range[0], publ_year_end=year_range[1])
    party_lines_df = party_lines_df[party_lines_df["company"] == polling_company]
    fig = px.line(party_lines_df, 
                    x="publdate", 
                    y="support", 
                    color="party", 
                    color_discrete_map=color_map,
                    labels=support_labels)

    return fig

@app.callback(
    dash.dependencies.Output('slider_label', 'children'),
    [dash.dependencies.Input('slider_hashtag_horizon', 'value')])
def update_output(value):
    return 'Trending hashtags during the last {0} days'.format(value)

@app.callback(
    Output("dropdown_hashtag", "options"),
    [Input("slider_hashtag_horizon", "value")]
)
def update_dropdown_hashtag(horizon):
    list_options = DataLoader.get_list_of_trending_hashtags(nr_of_days=horizon)
    new_options = [
        {"label": x, "value": x}
        for x in list_options]
    
    return new_options

@app.callback(
    Output("timeseries", "figure"),
    [Input("dropdown_hashtag", "value")]
)
def display_hashtag_timeseries(dropdown_hashtag):
    # Figure for hashtag timeseires
    hashtag_df = DataLoader.load_hashtags(filter=dropdown_hashtag)
    hashtag_df.sort_values(by="date", inplace=True)

    fig = px.line(hashtag_df,
                    x="date", 
                    y="count",
                    labels={
                        "date": "Date",
                        "count": "# of Tweets"
                    })
    return fig

# Machine Learning callbacks
@app.callback(
    Output("ml_prediction_bargraph", "figure"),
    Input("submit-val", 'n_clicks'),
    State("ml_radio", "value"),
    State("input-on-submit", "value")
)
def run_and_display_ml_predictions(n_clicks, ml_prediction_type, ml_text_input):    
    # Code for handling input and running predictions
    if ml_text_input is None:
        new_predictions_df = pd.DataFrame(
        {
            "party": ["M", "KD", "L", "C", "S", "MP", "V", "SD"],
            "likeness": [random.randint(0, 20) for i in range(8)]
        })
    else:
        processed_data = data_preprocessing(ml_text_input)
        new_predictions_df = load_and_predict_model("data/models/model.pkl", 
                                                    "data/models/pipe.pkl", 
                                                    processed_data)

    # Create the bar chart
    new_ml_bar = px.bar(new_predictions_df, 
                    x="party", 
                    y="likeness",
                    color="party",
                    color_discrete_map=color_map,
                    labels=support_labels)
    return new_ml_bar

@app.callback(
    [
        Output("party_bar", "figure"),
        Output("dropdown_polling_date", "options")
    ],
    [
        Input("dropdown_polling_company", "value"),
        Input("dropdown_polling_date", "value")]
)
def display_polling_bar(polling_company, polling_date):
    # Figure for polling bar chart
    temp_poll = polls[polls["company"] == polling_company]
    if polling_date:
        disp_poll = temp_poll[temp_poll["publdate"] == polling_date]
    else:
        disp_poll = temp_poll[temp_poll["publdate"] == temp_poll["publdate"].max()]

    pbar = px.bar(disp_poll, 
                    x="party", 
                    y="support", 
                    color="party",
                    color_discrete_map=color_map,
                    labels=support_labels)

    # Updating the options in the dropdown
    new_options=[
        {"label": datetime.utcfromtimestamp(x/1000000000).strftime("%Y-%m-%d"), 
        "value": datetime.utcfromtimestamp(x/1000000000).strftime("%Y-%m-%d") }
        for x in temp_poll.publdate.unique().tolist()
        ]
    
    return pbar, new_options


if __name__ == '__main__':
    import os
    #app.run_server(debug=True, host="0.0.0.0", port=8050)
    app.run_server(debug=True, host="0.0.0.0", port=os.getenv("PORT"))
