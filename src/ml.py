import pandas as pd
import joblib

def load_ml_model(model_path: str):
    model = joblib.load(model_path)

    return model

def get_tweets_from_twitter_handle(twitter_handle: str) -> str:
    # This function takes the twitter handle, scrapes the latests tweets
    # and then returns the tweets as one long text
    return True

def data_preprocessing(input_text: str) -> str:
    # This function takes raw text, preprocesses it and returns in format
    # for ML prediction
    return True