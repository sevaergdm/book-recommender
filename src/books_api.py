import argparse

import requests


def search_books_title_author(title, author):
    url = r"https://www.googleapis.com/books/v1/volumes"
    query = f'intitle:"{title}"+inauthor:"{author}"'
    params = {"q": query, "maxResults": 10}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return

    if data.get("totalItems", 0) == 0:
        print(f"No books were found with the title"
              f" '{title}' and author '{author}'")
        return

    books = data.get("items", [])
    search_author = author.lower().strip()

    filtered_books = [
        book for book in books
        if any(search_author in book_author.lower()
               for book_author in book.get("volumeInfo", {}).get("authors", [])
               )
    ]

    if not filtered_books:
        print(f"No books were found with the title"
              f" '{title}' and author '{author}'")

    return filtered_books


def print_book_info(books):
    for book in books:
        volume_info = book.get("volumeInfo", {})
        book_authors = ", ".join(volume_info.get("authors", []))
        book_title = volume_info.get("title", "N/A")
        publisher = volume_info.get("publisher", "N/A")
        published_date = volume_info.get("publishedDate", "N/A")
        main_category = volume_info.get("mainCategory", "N/A")
        categories = ", ".join(volume_info.get("categories", ["N/A"]))
        industry_identifiers = volume_info.get("industryIdentifiers", [])
        isbn13 = next(
            (item.get("identifier") for item in industry_identifiers
             if isinstance(item, dict) and item["type"] == "ISBN_13"),
            "N/A"
        )

        print("-" * 20)
        print(f"Title: {book_title}")
        print(f"Author(s): {book_authors}")
        print(f"Publisher: {publisher}")
        print(f"Published Date: {published_date}")
        print(f"Main Cateogry: {main_category}")
        print(f"Categories: {categories}")
        print(f"ISBN-13: {isbn13}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that accepts a title and author, then searches"
        " google books and returns the results"
    )
    parser.add_argument("--title", required=True, type=str)
    parser.add_argument("--author", required=True, type=str)
    args = parser.parse_args()

    books = search_books_title_author(args.title, args.author)
    print_book_info(books)
