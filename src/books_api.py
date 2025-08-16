import argparse
import re
from collections import Counter

import requests


def get_recommended_books_by_categories(categories, max_recommendations=10):
    if not categories:
        raise Exception("No categories provided to search by")

    master_books = {}

    for category in categories.keys():
        google_books = get_books_by_category_google(category, max_books_to_fetch=50)

        for book in google_books:
            isbn13 = book.get("isbn13")
            if isbn13:
                master_books_entry = master_books.setdefault(
                    isbn13, {"details": book, "matched_categories": []}
                )
                master_books_entry["matched_categories"].append(category)

    sorted_books = sorted(
        master_books.items(),
        key=lambda item: len(item[1]["matched_categories"]),
        reverse=True,
    )
    final_recommendations = [item[1]["details"] for item in sorted_books]

    return final_recommendations[:max_recommendations]


def get_books_by_category_google(category, max_books_to_fetch=200):
    raw_books = []
    url = r"https://www.googleapis.com/books/v1/volumes"
    batch_size = 40
    query = f'subject:"{category}"'

    for i in range(0, max_books_to_fetch, batch_size):
        params = {
            "q": query,
            "maxResults": batch_size,
            "startIndex": i,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

        if not data.get("items"):
            break

        raw_books.extend(data.get("items", []))

    if not raw_books:
        print(f"No books found with the category: {category}")
        return []

    book_dicts = []
    for book in raw_books:
        volume_info = book.get("volumeInfo", {})
        book_title = volume_info.get("title", "")
        book_authors = volume_info.get("authors", [])
        publisher = volume_info.get("publisher", "N/A")
        published_date = volume_info.get("publishedDate", "N/A")
        isbn13 = next(
            (
                item.get("identifier", "")
                for item in volume_info.get("industryIdentifiers", [])
                if isinstance(item, dict) and item.get("type", "") == "ISBN_13"
            ),
            None,
        )

        book_dict = {
            "isbn13": isbn13,
            "title": book_title,
            "authors": book_authors,
            "publisher": publisher,
            "published_date": published_date
        }
        book_dicts.append(book_dict)
    return book_dicts


def google_search_title_author(title, author, max_books_to_fetch=200):
    all_books = []
    url = r"https://www.googleapis.com/books/v1/volumes"
    batch_size = 40
    query = f'intitle:"{title}"+inauthor:"{author}"'

    for i in range(0, max_books_to_fetch, batch_size):
        params = {
            "q": query,
            "maxResults": batch_size,
            "startIndex": i,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            break

        if not data.get("items"):
            break

        all_books.extend(data.get("items", []))

    search_author = author.lower().strip()
    search_title = title.lower().strip()

    filtered_books = [
        book
        for book in all_books
        if (
            any(
                search_author in book_author.lower()
                for book_author in book.get("volumeInfo", {}).get("authors", [])
            )
            and search_title in book.get("volumeInfo", {}).get("title", "").lower()
        )
    ]

    if not filtered_books:
        print(f"No books were found with the title" f" '{title}' and author '{author}'")

    return filtered_books


def enrich_book_data_openlibrary(books):
    for book in books:
        isbn13 = next(
            (
                item.get("identifier", "")
                for item in book.get("volumeInfo", {}).get("industryIdentifiers", [])
                if isinstance(item, dict) and item.get("type", "") == "ISBN_13"
            ),
            None,
        )

        if isbn13:
            try:
                url = f"http://openlibrary.org/api/volumes/brief/isbn/{isbn13}.json"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                if "records" in data and data["records"]:
                    records_dict = data["records"]
                    records_data = list(records_dict.values())[0]
                    details = records_data.get("details", {}).get("details", {})
                    subjects = details.get("subjects", [])

                    book["openLibrarySubjects"] = subjects

            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data from OpenLibrary for ISBN {isbn13}: {e}")
    return books


def clean_and_split_categories(category_strings):
    cleaned_categories = []
    delimiters = ["&", "/", "-", ":", "and"]

    for raw_string in category_strings:
        temp_string = raw_string
        cleaned = re.sub(r"\(.*?\)", "", temp_string)
        cleaned = cleaned.replace("(", "").replace(")", "")
        for delimiter in delimiters:
            cleaned = cleaned.replace(delimiter, ",")

        subcategories = cleaned.split(",")
        for subcategory in subcategories:
            cleaned = subcategory.lower().strip()

            if "general" in cleaned:
                cleaned = cleaned.replace("general", "").strip()

            if cleaned:
                cleaned_categories.append(cleaned)

    return cleaned_categories


def get_book_categories(books, top_n=None):
    all_raw_categories = []

    for book in books:
        volume_info = book.get("volumeInfo", {})

        book_main_category = volume_info.get("mainCategory", "")
        book_categories_google = volume_info.get("categories", [])
        book_categories_google.append(book_main_category)

        book_categories_ol = book.get("openLibrarySubjects", [])

        all_raw_categories.extend(book_categories_google)
        all_raw_categories.extend(book_categories_ol)

    all_cleaned_categories = clean_and_split_categories(all_raw_categories)
    category_counts = Counter(all_cleaned_categories)
    sorted_categories = sorted(
        category_counts.items(), key=lambda item: item[1], reverse=True
    )

    if top_n is not None:
        sorted_categories = sorted_categories[:top_n]

    return dict(sorted_categories)


def print_book_info(books):
    for book in books:
        print("-" * 20)
        print(f'Title: {book.get("title", "")}')
        print(f'Author(s): {", ".join(book.get("authors", []))}')
        print(f'Publisher: {book.get("publisher", "")}')
        print(f'Published Date: {book.get("published_date", "")}')
        print(f'ISBN-13: {book.get("isbn13", "")}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script that accepts a title and author, then searches"
        " google books and returns the results"
    )
    parser.add_argument("--title", required=True, type=str)
    parser.add_argument("--author", required=True, type=str)
    args = parser.parse_args()

    books = google_search_title_author(args.title, args.author)
    books = enrich_book_data_openlibrary(books)
    #print_book_info(books)
    print("=" * 10 + "Book Categories Found" + "=" * 10)
    categories = get_book_categories(books)
    print(categories)
    print("=" * 10 + f"Recommended Books for '{args.title}' by {args.author}" + "="* 10)
    recommendations = get_recommended_books_by_categories(categories)
    print_book_info(recommendations)
#    american_fiction_books = get_books_by_category_google("paris")
#    print(american_fiction_books[:10])
