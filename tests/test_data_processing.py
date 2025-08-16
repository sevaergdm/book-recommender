import json

import pytest

from src.data_processing import (clean_and_split_categories,
                                 get_book_categories, print_book_info)


def test_clean_and_split_categories():
    raw_categories = [
        "Fiction",
        "Literature: Fiction",
        "Fiction, Literary",
        "Paris (France) -- Fiction",
        "General & American Fiction",
        "History of Europe",
        "Americana-general",
    ]

    expected_output = [
        "fiction",
        "literature",
        "fiction",
        "fiction",
        "literary",
        "paris",
        "fiction",
        "american fiction",
        "history of europe",
        "americana",
    ]

    cleaned = clean_and_split_categories(raw_categories)
    assert sorted(cleaned) == sorted(expected_output)


def test_clean_and_split_categories_empty():
    with pytest.raises(Exception) as e:
        clean_and_split_categories([])
    assert str(e.value) == "No categories provided"


def test_get_book_categories():
    expected_output = {
        "fiction": 8,
        "spain": 2,
        "history": 2,
        "civil war": 2,
        "1936": 2,
        "1939": 2,
        "americans": 2,
        "classics": 2,
        "american fiction": 1,
        "war stories": 1,
        "literature": 1,
        "criticism": 1,
        "children": 1,
        "young adult": 1,
        "war": 1,
        "military": 1,
        "audiobooks": 1,
    }

    with open("book_sample.json", "r") as f:
        books = json.load(f)
        categories = get_book_categories(books)

    assert categories == expected_output


def test_get_book_categories_empty():
    with pytest.raises(Exception) as e:
        get_book_categories([])
    assert str(e.value) == "No books provided"


def test_print_book_info(capsys):
    books = [
        {
            "isbn13": 12345,
            "title": "A book",
            "authors": ["John Doe"],
            "publisher": "Publishing",
            "published_date": "2020-02-02",
        },
        {
            "isbn13": 67890,
            "title": "A book 2",
            "authors": ["Jane Doe"],
            "publisher": "Publishing House",
            "published_date": "1990-02-02",
        },
    ]

    print_book_info(books)

    captured = capsys.readouterr()
    output = captured.out

    assert "Title: A book" in output
    assert "Author(s): John Doe" in output
    assert "Publisher: Publishing" in output
    assert "Published Date: 2020-02-02" in output
    assert "ISBN-13: 12345" in output
