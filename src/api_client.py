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
