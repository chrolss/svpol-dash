import dash
import dash_core_components as dcc
from dash_core_components.Dropdown import Dropdown
from dash_core_components.DatePickerRange import DatePickerRange
from dash_core_components.RadioItems import RadioItems
from dash_core_components.Textarea import Textarea
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import date
from src.data import load_from_db
from src.ml import load_ml_model, data_preprocessing

app = dash.Dash(__name__)

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

# Machine learning baseline
ml_baseline = pd.DataFrame(
    {
        "party": ["M", "KD", "L", "C", "S", "MP", "V", "SD"],
        "likeness": [10, 10, 10, 10, 10, 10, 10, 10,]
    })
ml_bar = px.bar(ml_baseline, 
                x="party", 
                y="likeness")

# Load Machine Learning model
#model = load_ml_model("data/models/test_model.pkl")

# Load hashtag data
hashtags = load_from_db("hashtags")
hashtags["date"] = pd.to_datetime(hashtags["date"])

# Load party poll numbers
polls = pd.read_pickle("/home/chrolss/PycharmProjects/svpol/data/partisympatier.pkl")

# Begin app layout
app.layout = html.Div(children=[
    html.H1(children='#svpol analytics'),

    html.Div(children='''
        #svpol: Explore the world of Swedish political Twitter.
    '''),

    # Machine Learning part of the app
    html.Div([
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
        dcc.Dropdown(
            id="dropdown_hashtag",
            options=[{"label": x, "value": x} 
                    for x in hashtags["hashtag"].unique().tolist()[0:10]],
            value="#svpol",
            clearable=False,
        )
    ], style={'width': '33%', 'display': 'inline-block'}
    ),

    dcc.Graph(id="timeseries"),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id="dropdown_polling_company",
                options=[{"label": x, "value": x}
                    for x in polls.company.unique().tolist()],
                value="Sifo",
                clearable=False
            ),
        ],style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id="dropdown_polling_date",
                clearable=False
            )
        ],style={'width': '33%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(
        id="party_bar"
    ),

    html.Div([
        # Change to rangeslider and do some datetime magic to make it look better
        dcc.DatePickerRange(
            id="datepicker_party_lines",
            min_date_allowed=date(2000, 1, 1),
            max_date_allowed=date(2021, 10, 30),
            initial_visible_month=date(2017, 8, 5),
            end_date=date(2017, 8, 25)
        ),
        dcc.Graph(
            id="party_lines",
            figure = px.line(polls, x="publdate", y="support", color="party")
        )
    ])
])

# Callbacks
@app.callback(
    Output("timeseries", "figure"),
    [Input("dropdown_hashtag", "value")]
)
def display_hashtag_timeseries(dropdown_hashtag):
    # Figure for hashtag timeseires
    hashtag_df = hashtags[hashtags["hashtag"] == dropdown_hashtag]
    hashtag_df.sort_values(by="date", inplace=True)

    fig = px.line(hashtag_df, x="date", y="count")
    return fig

# Machine Learning callbacks
@app.callback(
    Output("ml_prediction_bargraph", "figure"),
    [Input("submit-val", 'n_clicks')],
    state=[State("ml_radio", "value"),
           State("input-on-submit", "value")]
)
def run_and_display_ml_predictions(n_clicks, ml_prediction_type, ml_text_input):
    # Temporary for site functionality
    import random
    new_predictions_df = pd.DataFrame(
    {
        "party": ["M", "KD", "L", "C", "S", "MP", "V", "SD"],
        "likeness": [random.randint(0, 100) for i in range(8)]
    })
    # Code for handling input and running predictions
    #processed_data = data_preprocessing(ml_text_input)
    #predictions = model.predict_proba(processed_data)
    #predictions_df = pd.DataFrame({
    #    "party": ["M", "KD", "L", "C", "S", "MP", "V", "SD"],
    #    "likeness": [0, 0, 0, 0, 0, 0, 0, 0,]
    #})

    # Create the bar chart
    new_ml_bar = px.bar(new_predictions_df, 
                    x="party", 
                    y="likeness")
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
                    color_discrete_map=color_map)

    # Updating the options in the dropdown
    from datetime import datetime
    new_options=[
        {"label": datetime.utcfromtimestamp(x/1000000000).strftime("%Y-%m-%d"), 
        "value": datetime.utcfromtimestamp(x/1000000000).strftime("%Y-%m-%d") }
        for x in temp_poll.publdate.unique().tolist()
        ]
    
    return pbar, new_options


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
