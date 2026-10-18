The goal of this project is to learn the basics of how to work with data.
*AI was used with the aim of improving project structure, adding general safety nets, improving user experience and generating proper README files.*

# Reviews Sentiment Classifier

Classifies the sentiments expressed in product reviews using the Gemini API.
For each review it returns up to three sentiments (e.g. `enjoyment`, `disappointment`)
chosen from a fixed vocabulary, and saves the results to a CSV file.

It is designed for large datasets: reviews are sent in batches, failed requests
are retried, progress is saved after every batch and an interrupted run can be resumed.

## How it works

```
reviews (.jsonl) → batches of 25 → Gemini (JSON answer with a fixed schema) → outputs/results.csv
```

1. `src/data.py` reads the first `n` reviews (`rating`, `title`, `text`).
2. `src/prompt.py` builds a prompt for each batch. Every review is sent with its `id`.
3. `src/classifier.py` asks Gemini for a JSON answer that follows a schema
   (`id` + list of sentiments), keeps only the allowed sentiments and matches each
   answer to its review by `id`.
4. Reviews that the model skipped are requested again (up to 3 attempts).
   Rate-limit errors (429) and server errors (5xx) wait and retry.
5. After every batch the results are written to the output file.

## Requirements

- Python 3.10 or newer
- A Gemini API key (a free one can be created in [Google AI Studio](https://aistudio.google.com/))

## Installation

```bash
git clone https://github.com/Venignuss/ReviewsSentimentClassifier
cd ReviewsSentimentClassifier

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create your `.env` file from the example and add your key:

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git. Never commit your key.

## Data

The repository includes a 100-review sample (`data/sample.jsonl`), so you can run the
program right away. The full dataset is not included: see [`data/README.md`](data/README.md)
for how to download it.

## Usage

```bash
python main.py                                      # sample, 100 reviews
python main.py --input data/dataset.jsonl -n 1000   # full dataset, first 1000 reviews
python main.py --resume                             # continue an interrupted run / retry failed reviews
python main.py --help
```

| Option | Default | Description |
|---|---|---|
| `--input` | `data/sample.jsonl` | JSON Lines file with the reviews |
| `-n` | `100` | Number of reviews to classify |
| `--output` | `outputs/results.csv` | CSV file for the results |
| `--model` | `gemini-flash-latest` | Gemini model to use |
| `--batch-size` | `25` | Reviews per request |
| `--resume` | off | Skip the reviews already in the output file |

Press `Ctrl+C` at any time: what has been classified is already saved, and you can
continue later with `--resume`.

## Output

`outputs/results.csv` has one row per review. `id` is the position of the review in the
input file, and `s1`–`s3` are its sentiments, most prominent first (empty if the review
expresses fewer than three):

```csv
id,s1,s2,s3
0,anger,distrust,
1,enjoyment,satisfaction,
2,enthusiasm,delight,
```

To join the sentiments with the review text, load both and join them by `id`
(the reviews DataFrame returned by `load_reviews` uses the same index).

## Project structure

```
├── main.py              Command line entry point
├── src/
│   ├── data.py          Loads and validates the reviews
│   ├── prompt.py        Builds the prompt and defines the allowed sentiments
│   └── classifier.py    Calls Gemini, retries and saves the results
├── data/                Sample reviews and instructions to get the full dataset
├── outputs/             Results (CSV)
├── notebooks/           Notebook to analyse the results
├── requirements.txt
└── .env.example
```

## Customisation

- **Sentiments:** edit the `SENTIMENTS` list in `src/prompt.py`. Using a closed list
  keeps the labels consistent between batches.
- **Number of sentiments per review:** the `max_sentiments` parameter of `classify_all`
  (default 3).

## Notes

- Free-tier limits of the Gemini API (requests per minute and per day) change over time.
  Check them in Google AI Studio. Smaller batches or `--resume` help when you hit them.
- The review texts are sent to Google's servers. Do not use this with private or
  sensitive data.
- Model names change over time. If `gemini-flash-latest` stops working, pass another
  one with `--model`.

## Credits

Reviews come from the Amazon Reviews 2023 dataset (McAuley Lab, UCSD).
See [`data/README.md`](data/README.md) for the citation.