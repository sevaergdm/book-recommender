import argparse
import json

from src.api_client import google_search_title_author, enrich_book_data_openlibrary


def get_sample_books(title, author, max_books_to_fetch=5):
    books = google_search_title_author(title, author, max_books_to_fetch)
    enriched_books = enrich_book_data_openlibrary(books)

    with open(f"book_sample.json", "w") as f:
        json.dump(enriched_books, f, indent=2)

    print(f"Saved {len(enriched_books)} items to book_sample.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that accepts a title and author, then searches"
        " google books and writes the results to a json file"
    )
    parser.add_argument("--title", required=True, type=str)
    parser.add_argument("--author", required=True, type=str)
    args = parser.parse_args()

    get_sample_books(args.title, args.author)
