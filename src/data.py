import pandas as pd
from pathlib import Path

REQUIRED_COLUMNS = ["rating", "title", "text"]


def load_reviews(path: str | Path, n: int = 100) -> pd.DataFrame:
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {path}. See data/README.md to download it, "
            "or use the sample in data/sample.jsonl."
        )

    if n < 1:
        raise ValueError(f"n must be at least 1 (got {n}).")

    df = pd.read_json(path, lines = True, nrows = n)

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing:
        raise ValueError(
            f"The dataset is missing the column(s): {', '.join(missing)}. "
            f"Columns found: {', '.join(df.columns)}."
        )
    
    df = df[REQUIRED_COLUMNS].fillna("")
    df.index.name = "id"

    return df