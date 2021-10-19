from dataclasses import dataclass
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine


def _to_datetime(datestring: str):
        return datetime.strptime(datestring, "%Y-%m-%d")

@dataclass
class DataLoader:
    engine_url = "sqlite:///data/tweets.db"

    
    def select_all_from_db(self, table: str):
        engine = create_engine(self.engine_url)
        con = engine.connect()
        query = "SELECT * FROM {0}".format(table)
        res = con.execute(query)

        return pd.DataFrame(data=res.fetchall(), columns=res.keys())

    def load_hashtags(self, start_date: str = "1900-01-01", end_date:str = "9999-12-31", filter:str = "None"):
        raw_data = self.select_all_from_db(table="hashtags")
        raw_data = raw_data[(raw_data["date"] >= start_date) & (raw_data["date"] <= end_date)]
        raw_data["date"] = pd.to_datetime(raw_data["date"])
        if filter != "None":
            return raw_data[raw_data["hashtag"] == filter]
        else:
            return raw_data
    
    def get_list_of_trending_hashtags(self, nr_of_days: int = 365, nr_of_hashtags: int = 10):
        start_date_dt = datetime.today() - timedelta(days=nr_of_days)
        start_date_txt = datetime.strftime(start_date_dt, "%Y-%m-%d")
        hashtags = self.load_hashtags(start_date=start_date_txt)
        trending_hashtags = hashtags.groupby("hashtag").sum("count").sort_values(by="count", ascending=False)

        return trending_hashtags.iloc[0:nr_of_hashtags].index.to_list()

    def load_party_poll_numbers(self, publ_year_start: str = "2000", publ_year_end: str = "2022"):
        polls = pd.read_pickle("data/partisympatier.pkl")
        return polls[
            (polls["publdate"] >= _to_datetime("{0}-01-01".format(publ_year_start))) 
            & 
            (polls["publdate"] <= _to_datetime("{0}-12-31".format(publ_year_end)))]
