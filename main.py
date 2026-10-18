import argparse
import os
import sys
 
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
 
from src import classifier, data
 
DEFAULT_MODEL = "gemini-flash-latest"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description = "Classify the sentiments of product reviews with Gemini."
    )
    parser.add_argument("--input", default = "data/sample.jsonl",
                        help = "JSON Lines file with the reviews (default: %(default)s)")
    parser.add_argument("-n", type = int, default = 100,
                        help = "number of reviews to classify (default: %(default)s)")
    parser.add_argument("--output", default = "outputs/results.csv",
                        help = "CSV file for the results (default: %(default)s)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Gemini model (default: %(default)s)")
    parser.add_argument("--batch-size", type=int, default=25,
                        help="reviews per request (default: %(default)s)")
    parser.add_argument("--resume", action="store_true",
                        help="skip the reviews already in the output file")

    return parser.parse_args()

def main() -> None:
    args = parse_args()

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Missing GEMINI_API_KEY. Copy .env.example to .env and set your API key.")

    try:
        reviews = data.load_reviews(args.input, args.n)
    except (FileNotFoundError, ValueError) as error:
        sys.exit(f"Error: {error}")

    client = genai.Client(api_key = api_key)
    print(f"Classifying {len(reviews)} reviews with {args.model}...")

    try:
        results, failed = classifier.classify_all(
            reviews,
            client,
            model=args.model,
            batch_size=args.batch_size,
            checkpoint=args.output,
            resume=args.resume
        )
    except genai_errors.APIError as error:
        sys.exit(f"Gemini API error({error.code}): {error.message}")
    except KeyboardInterrupt:
        sys.exit(f"\nInterrupted. Progress saved in {args.output}. "
                 "Run again with --resume to continue.")

    print(f"Done: {len(results)} reviews classified. Results in {args.output}")
    if failed:
        shown = ", ".join(map(str, failed[:20]))
        extra = "..." if len(failed) > 20 else ""
        print(f"Warning: {len(failed)} reviews failed (ids: {shown}{extra}). "
              "Run again with --resume to retry them.")

if __name__ == "__main__":
    main()
