# Data

The full dataset is **not** included in this repository (it is more than 1 GB).
This folder only contains a small sample so the project can be tried right away.

## Files

| File | In the repo? | What it is |
|---|---|---|
| `sample.jsonl` | Yes | The first 100 reviews of the dataset, for quick tests |
| `dataset.jsonl` | No (ignored by Git) | The full dataset, which you download yourself |

## Dataset

[Amazon Reviews 2023](https://amazon-reviews-2023.github.io/), by the McAuley Lab (UCSD).
Each line of the `.jsonl` file is one review. This project only uses three fields:

| Field | Description |
|---|---|
| `rating` | Stars, from 1.0 to 5.0 |
| `title` | Title of the review |
| `text` | Body of the review |

The other fields (`asin`, `user_id`, `timestamp`, `helpful_vote`...) are ignored.

## Download the full dataset

1. Pick a category from the [dataset page](https://amazon-reviews-2023.github.io/).
   This project was run with: **`Software`**.
2. From the project root, download it, decompress it and place it in `data/`:

   ```bash
   curl -O https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/<CATEGORY>.jsonl.gz
   gunzip <CATEGORY>.jsonl.gz
   mv <CATEGORY>.jsonl data/dataset.jsonl
   ```

3. Run the program on it:

   ```bash
   python main.py --input data/dataset.jsonl -n 100
   ```

The program only reads the first `n` reviews, so it never loads the whole file into memory.

## Recreate the sample

```bash
head -n 100 data/dataset.jsonl > data/sample.jsonl
```

## Citation

If you use this data, cite the authors:

> Yupeng Hou, Jiacheng Li, Zhankui He, An Yan, Xiusi Chen, Julian McAuley.
> *Bridging Language and Items for Retrieval and Recommendation.* arXiv:2403.03952, 2024.