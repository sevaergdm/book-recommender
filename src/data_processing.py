import re
from collections import Counter


def clean_and_split_categories(category_strings):
    if not category_strings:
        raise Exception("No categories provided")

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
    if not books:
        raise Exception("No books provided")

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
