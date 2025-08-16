from api_client import get_books_by_category_google


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
