import argparse
from api_client import google_search_title_author, enrich_book_data_openlibrary
from data_processing import get_book_categories, print_book_info
from recommendation_engine import get_recommended_books_by_categories


def main():
    parser = argparse.ArgumentParser(
        description="Script that accepts a title and author, then searches"
        " google books and returns the results"
    )
    parser.add_argument("--title", required=True, type=str)
    parser.add_argument("--author", required=True, type=str)
    args = parser.parse_args()

    books = google_search_title_author(args.title, args.author)
    books = enrich_book_data_openlibrary(books)
    
    print("=" * 10 + "Book Categories Found" + "=" * 10)
    categories = get_book_categories(books)
    
    print(categories)
    print("=" * 10 + f"Recommended Books for '{args.title}' by {args.author}" + "="* 10)
    recommendations = get_recommended_books_by_categories(categories)
    print_book_info(recommendations)


if __name__ == "__main__":
    main()
