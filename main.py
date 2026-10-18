import json
import pandas as pd

df = pd.read_json("dataset.jsonl", lines = True, nrows=5)

df = df[["rating", "title", "text"]]