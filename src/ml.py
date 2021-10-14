import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk import TweetTokenizer
import lemmy


def load_and_predict_model(model_path: str, cv_path: str, input_text: str):
    model = joblib.load(model_path)
    cv = joblib.load(cv_path)

    word_vector = cv.transform([input_text])
    predictions = model.predict_proba(word_vector)

    pred_df = pd.DataFrame({
        "party": model.classes_.tolist(),
        "likeness": (predictions[0]*100).tolist()
    })

    return pred_df

def get_tweets_from_twitter_handle(twitter_handle: str) -> str:
    # This function takes the twitter handle, scrapes the latests tweets
    # and then returns the tweets as one long text
    return True

def data_preprocessing(input_text: str) -> str:
    # This function takes raw text, preprocesses it and returns in format
    # for ML prediction
    # Load nltk stuff

    # Download nltk stuff for stopwords, nltk.download(corpus?)
    dataframe = False
    stopword = stopwords.words("swedish")
    lem = lemmy.load("sv")
    twtknizer = TweetTokenizer()

    # Create a lemmatized column
    def remove_punctuations(input_text):
        chars_to_remove = [".", "!", "?", ",", ":", ";"]
        for special_char in chars_to_remove:
            input_text = input_text.replace(special_char, "")
        return input_text
    if dataframe:
        df = pd.DataFrame() # Empty frame for now
        df["tweets"] = df["tweets"].apply(lambda x: remove_punctuations(x))
        df["word_tokens"] = df["tweets"].apply(lambda x: twtknizer.tokenize(x))
        df["lemmatized"] = df["word_tokens"].apply(lambda y: [lem.lemmatize("NOUN", word)[0] for word in y])
        df["tweets_lemma"] = df["lemmatized"].apply(lambda z: " ".join(z))
    else:
        input_text = remove_punctuations(input_text)
        word_tokens = twtknizer.tokenize(input_text)
        lemmatized_tokens = [lem.lemmatize("NOUN", word)[0] for word in word_tokens]
        prediction_text = " ".join(lemmatized_tokens)

    return prediction_text