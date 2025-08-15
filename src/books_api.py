import argparse
import re

import requests


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
        for delimiter in delimiters:
            temp_string = temp_string.replace(delimiter, ",")

        subcategories = temp_string.split(",")
        for subcategory in subcategories:
            cleaned = subcategory.lower().strip()
            cleaned = re.sub(r"\(.*?\)", "", cleaned)
            cleaned.replace("(", "").replace(")", "")

            if "general" in cleaned:
                cleaned = cleaned.replace("general", "").strip()

            if cleaned:
                cleaned_categories.append(cleaned)

    return sorted(list(set(cleaned_categories)))


def get_book_categories(books):
    all_raw_categories = []

    for book in books:
        volume_info = book.get("volumeInfo", {})

        book_main_category = volume_info.get("mainCategory", "")
        book_categories_google = volume_info.get("categories", [])
        book_categories_google.append(book_main_category)

        book_categories_ol = book.get("openLibrarySubjects", [])

        all_raw_categories.extend(book_categories_google)
        all_raw_categories.extend(book_categories_ol)

    return clean_and_split_categories(all_raw_categories)


def print_book_info(books):
    for book in books:
        volume_info = book.get("volumeInfo", {})
        book_authors = ", ".join(volume_info.get("authors", []))
        book_title = volume_info.get("title", "N/A")
        publisher = volume_info.get("publisher", "N/A")
        published_date = volume_info.get("publishedDate", "N/A")
        main_category = volume_info.get("mainCategory", "N/A")
        categories = ", ".join(volume_info.get("categories", ["N/A"]))
        ol_subjects = ", ".join(book.get("openLibrarySubjects", ["N/A"]))
        industry_identifiers = volume_info.get("industryIdentifiers", [])
        isbn13 = next(
            (
                item.get("identifier")
                for item in industry_identifiers
                if isinstance(item, dict) and item["type"] == "ISBN_13"
            ),
            "N/A",
        )

        print("-" * 20)
        print(f"Title: {book_title}")
        print(f"Author(s): {book_authors}")
        print(f"Publisher: {publisher}")
        print(f"Published Date: {published_date}")
        print(f"Main Cateogry: {main_category}")
        print(f"Categories: {categories}")
        print(f"Open Library Subjects: {ol_subjects}")
        print(f"ISBN-13: {isbn13}")


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
    print_book_info(books)
    print("=" * 10 + "Book Categories" + "=" * 10)
    print(get_book_categories(books))
