import pandas as pd

SENTIMENTS = [
    "anger",
    "annoyance",
    "disappointment",
    "distrust",
    "frustration",
    "indifference",
    "enjoyment",
    "satisfaction",
    "enthusiasm",
    "delight",
    "gratitude",
    "surprise",
    "confusion",
    "regret",
]

def build_prompt(df: pd.DataFrame, max_sentiments: int = 3) -> str:
    reviews = df[["rating", "title", "text"]].to_csv(index_label="id")

    return (
        "For each review below, identify the sentiments it expresses, "
        "based only on its rating, title and text.\n"
        f"- Return between 1 and {max_sentiments} sentiments per review, "
        "the most prominent one first.\n"
        f"- Use only these sentiments: {', '.join(SENTIMENTS)}.\n"
        "- Return exactly one entry per review, using the review's id.\n\n"
        f"Reviews (CSV):\n{reviews}"
    )