from unittest.mock import patch

import pytest

from src.recommendation_engine import get_recommended_books_by_categories


@patch("src.recommendation_engine.get_books_by_category_google")
def test_get_recommended_books_by_categories(mock_get_books_by_category):
    categories = {"Fiction": None, "Action": None}

    mock_get_books_by_category.side_effect = [
        [
            {"isbn13": "111", "title": "Some Book"},
            {"isbn13": "222", "title": "Another Book"},
        ],
        [
            {"isbn13": "333", "title": "Yet Another Book"},
            {"isbn13": "222", "title": "Another Book"},
        ],
    ]

    result = get_recommended_books_by_categories(categories, max_recommendations=5)

    assert len(result) == 3
    assert result[0]["isbn13"] == "222"
    assert {book["isbn13"] for book in result} == {"111", "222", "333"}
    assert mock_get_books_by_category.call_count == 2
    mock_get_books_by_category.assert_any_call("Fiction", max_books_to_fetch=50)
    mock_get_books_by_category.assert_any_call("Action", max_books_to_fetch=50)


def test_get_recommended_books_by_categories_empty():
    with pytest.raises(Exception, match="No categories provided to search by"):
        get_recommended_books_by_categories({})
