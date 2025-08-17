from unittest.mock import MagicMock, patch

import requests

from src.api_client import (enrich_book_data_openlibrary,
                            get_books_by_category_google,
                            google_search_title_author)


@patch("src.api_client.requests.get")
def test_google_search_title_author(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "For Whom the Bell Tolls",
                    "authors": ["Ernest Hemingway"],
                    "publishedDate": "1940-10-21",
                    "industryIdentifiers": [
                        {"type": "ISBN_10", "identifier": "238226294X"},
                        {"type": "ISBN_13", "identifier": "9782382262948"},
                    ],
                    "categories": ["Fiction"],
                }
            }
        ],
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None

    mock_get.return_value = mock_response

    books = google_search_title_author(
        "For Whom the Bell Tolls", "Ernest Hemingway", max_books_to_fetch=1
    )

    assert len(books) == 1
    assert books[0]["volumeInfo"]["title"] == "For Whom the Bell Tolls"
    mock_get.assert_called()


@patch("src.api_client.requests.get")
def test_google_search_title_author_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    books = google_search_title_author(
        "For Whom the Bell Tolls", "Ernest Hemingway", max_books_to_fetch=1
    )

    assert books == []
    mock_get.assert_called()


@patch("src.api_client.requests.get")
def test_google_search_title_author_exception_no_results(mock_get, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = {"items": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None

    mock_get.return_value = mock_response

    books = google_search_title_author(
        "For Whom the Bell Tolls", "Ernest Hemingway", max_books_to_fetch=1
    )
    captured = capsys.readouterr()

    assert len(books) == 0
    assert (
        "No books were found with the title 'For Whom the Bell Tolls' and author 'Ernest Hemingway'"
        in captured.out
    )
    mock_get.assert_called()


@patch("src.api_client.requests.get")
def test_enrich_book_data_openlibrary(mock_get):
    books_input = [
        {
            "volumeInfo": {
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9782382262948"}
                ]
            }
        }
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "records": {
            "some_key": {"details": {"details": {"subjects": ["Fiction", "Action"]}}}
        }
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None
    mock_get.return_value = mock_response

    result = enrich_book_data_openlibrary(books_input)

    assert len(result) == 1
    assert result[0]["openLibrarySubjects"] == ["Fiction", "Action"]
    mock_get.assert_called_once_with(
        "http://openlibrary.org/api/volumes/brief/isbn/9782382262948.json"
    )


@patch("src.api_client.requests.get")
def test_enrich_book_data_openlibrary_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    books_input = [
        {
            "volumeInfo": {
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9782382262948"}
                ]
            }
        }
    ]
    books = enrich_book_data_openlibrary(books_input)

    assert books == books_input
    mock_get.assert_called()


@patch("src.api_client.requests.get")
def test_get_books_by_category_google(mock_get):
    sample_api_response = {
        "items": [
            {
                "volumeInfo": {
                    "title": "For Whom the Bell Tolls",
                    "authors": ["Ernest Hemingway"],
                    "publishedDate": "1940-10-21",
                    "industryIdentifiers": [
                        {"type": "ISBN_10", "identifier": "238226294X"},
                        {"type": "ISBN_13", "identifier": "9782382262948"},
                    ],
                    "categories": ["Fiction"],
                }
            }
        ],
    }

    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_response
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None
    mock_get.return_value = mock_response

    result = get_books_by_category_google("Fiction", max_books_to_fetch=1)

    assert result[0]["isbn13"] == "9782382262948"
    assert result[0]["title"] == "For Whom the Bell Tolls"
    mock_get.assert_called()


@patch("src.api_client.requests.get")
def test_get_books_by_category_google_exception(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    books = get_books_by_category_google("Fiction", max_books_to_fetch=1)

    assert books == []
    mock_get.assert_called()


@patch("src.api_client.requests.get")
def test_get_books_by_category_google_empty(mock_get, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = {"items": []}
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None
    mock_get.return_value = mock_response

    result = get_books_by_category_google("Fiction", max_books_to_fetch=1)
    captured = capsys.readouterr()

    assert result == []
    assert "No books found with the category: Fiction" in captured.out
    mock_get.assert_called()
