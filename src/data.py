import pandas as pd
from sqlalchemy import create_engine

def load_from_db(table: str):
    engine = create_engine("sqlite:///data/tweets.db")
    con = engine.connect()
    query = "SELECT * FROM {0}".format(table)
    res = con.execute(query)

    return pd.DataFrame(data=res.fetchall(), columns=res.keys())
