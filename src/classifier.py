import time
from pathlib import Path
 
import pandas as pd
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel
from tqdm import tqdm
from typing import cast

from src.prompt import SENTIMENTS, build_prompt

class ReviewSentiments(BaseModel):
    """Format of the answer for ONE review (Gemini is forced to follow it)."""
    id: int
    sentiments: list[str]

def classify_batch(
        df: pd.DataFrame, client: genai.Client, model: str, max_sentiments: int = 3
) -> dict[int, list[str]]:
    """Classify a batch of reviews with one request.
 
    Returns {review id: [sentiments]}. The ids the model skipped are not in it.
    """

    response = client.models.generate_content(
        model = model,
        contents = build_prompt(df, max_sentiments),
        config = types.GenerateContentConfig(
            response_mime_type = "application/json",
            response_schema = list[ReviewSentiments],
            temperature = 0
        )
    )

    parsed = response.parsed
    if not isinstance(parsed, list):
        return {}
    items = cast(list[ReviewSentiments], parsed)

    return {
        item.id: [s for s in item.sentiments if s in SENTIMENTS][:max_sentiments]
        for item in items
        if item.id in df.index
    }

def to_frame(results: dict[int, list[str]], max_sentiments: int) -> pd.DataFrame:
    columns = [f"s{i}" for i in range(1, max_sentiments + 1)]
    rows = {i: s + [None] * (max_sentiments - len(s)) for i,s in results.items()}
    frame = pd.DataFrame.from_dict(rows, orient="index", columns=columns)
    frame.index.name = "id"
    return frame.sort_index()

def classify_all(
        df: pd.DataFrame,
        client: genai.Client,
        model: str,
        batch_size: int = 25,
        max_sentiments: int = 3,
        retries: int = 3,
        checkpoint: str | Path | None = None,
        resume: bool = False
) -> tuple[pd.DataFrame, list[int]]:
    
    """Classify all the reviews, batch by batch.

    Returns (DataFrame with s1..sN indexed by id, ids that failed).
    If `checkpoint` is given, the results are saved there after every batch;
    with resume=True, the ids already in that file are skipped.
    """

    results: dict[int, list[str]] = {}
    if checkpoint:
        checkpoint = Path(checkpoint)
        checkpoint.parent.mkdir(parents = True, exist_ok = True)
        if resume and checkpoint.exists():
            saved = pd.read_csv(checkpoint, index_col = "id")
            for review_id, *sentiments in saved.reset_index().itertuples(index=False):
                results[int(review_id)] = [s for s in sentiments if isinstance(s, str)]

    todo = [int(i) for i in df.index if int(i) not in results]
    failed = []

    for start in tqdm(range(0, len(todo), batch_size), desc = "Classifying", unit = "batch"):
        pending = todo[start: start + batch_size]

        for attempt in range(retries):
            try:
                results.update(classify_batch(df.loc[pending], client, model, max_sentiments))
            except genai_errors.APIError as error:
                if error.code != 429 and error.code <= 500:
                    raise
                time.sleep(5 * 2**attempt)

            pending = [i for i in pending if i not in results]

            if not pending:
                break

        failed.extend(pending)
        if checkpoint:
            to_frame(results, max_sentiments).to_csv(checkpoint, encoding = "utf-8")

    return to_frame(results, max_sentiments), failed