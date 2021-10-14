import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
from src.data import load_from_db
from src.ml import load_and_predict_model, data_preprocessing
import plotly.io as pio

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

# Machine learning baseline
ml_baseline = pd.DataFrame(
    {
        "party": ["M", "KD", "L", "C", "S", "MP", "V", "SD"],
        "likeness": [10, 10, 10, 10, 10, 10, 10, 10,]
    })
ml_bar = px.bar(ml_baseline, 
                x="party", 
                y="likeness")

# Load hashtag data
hashtags = load_from_db("hashtags")
hashtags["date"] = pd.to_datetime(hashtags["date"])

# Load party poll numbers
polls = pd.read_pickle("data/partisympatier.pkl")

# Begin app layout
app.layout = html.Div(children=[
    html.H1(children='Analysis of #svpol: Explore the World of Swedish Political Twitter'),

    # Empty spacer
    html.Div([]),

    # Machine Learning part of the app
    html.Div([
        html.H3(children="Predict political leanings in Swedish text"),
        dcc.RadioItems(id="ml_radio",
        options=[
            {"label": "Twitter handle", "value": "twitter_handle"},
            {"label": "Free text", "value": "free_text"} 
        ],
        value="twitter_handle"
        ),
        html.Div(
            dcc.Input(id='input-on-submit', type='text')),
            html.Button('Predict', id='submit-val', n_clicks=0),
            html.Div(id='container-button-basic',children='Enter a value and press submit')
    ]),
    # Div that holds the ML outputs - bar chart
    html.Div([
        dcc.Graph(id="ml_prediction_bargraph",
        figure=ml_bar)
    ]),

    # Statistical part of the app
    html.Div([
        html.H3(children="Hashtag mentions over time"),
        dcc.Dropdown(
            id="dropdown_hashtag",
            options=[{"label": x, "value": x} 
                    for x in hashtags["hashtag"].unique().tolist()[0:10]],
            value="#svpol",
            clearable=False,
            style = {"color": "black"},
        )
    ], style={'width': '33%', 'display': 'inline-block'}
    ),

    dcc.Graph(id="timeseries"),

    html.Div([
        html.H3(children="Party Support from polling institutes"),
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
        # Change to rangeslider and do some datetime magic to make it look better
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
                value=[2000, 2011]
            )
        ], style={'width': '66%', 'display': 'inline-block', "color": "white"}),

        dcc.Graph(
            id="party_lines"
            #figure = px.line(polls[polls["publdate"] > "1900-01-01"], x="publdate", y="support", color="party")
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
    party_lines_df = polls[(polls["publdate"] >= "{0}-01-01".format(year_range[0])) & (polls["publdate"] <= "{0}-12-31".format(year_range[1]))]
    party_lines_df = party_lines_df[party_lines_df["company"] == polling_company]
    fig = px.line(party_lines_df, 
                    x="publdate", 
                    y="support", 
                    color="party", 
                    color_discrete_map=color_map,
                    labels=support_labels)

    return fig

@app.callback(
    Output("timeseries", "figure"),
    [Input("dropdown_hashtag", "value")]
)
def display_hashtag_timeseries(dropdown_hashtag):
    # Figure for hashtag timeseires
    hashtag_df = hashtags[hashtags["hashtag"] == dropdown_hashtag]
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
    import random
    if ml_text_input is None:
        new_predictions_df = pd.DataFrame(
        {
            "party": ["M", "KD", "L", "C", "S", "MP", "V", "SD"],
            "likeness": [random.randint(0, 100) for i in range(8)]
        })
    else:
        processed_data = data_preprocessing(ml_text_input)
        new_predictions_df = load_and_predict_model("data/models/model.pkl", "data/models/cv.pkl", processed_data)

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
