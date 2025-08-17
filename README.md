# Book Recommender

My first attempt at building simple recommendation service which takes a book supplied by the user and attempts to find a set of recommendations for other books to read.

There are many things that would need to be improved to make this more realistically functional, but I am using this as a simple learning opportunity. I may come back and revisit in the future to see if I can figure out the more fun bits.

## Usage

`python3 src/main.py --title="{BOOK_TITLE}" --author="{BOOK AUTHOR}"`

## What it does

This takes a very naive and unscientific approach to recommendations:

* Look up the supplied book in the [Google Books API](https://developers.google.com/books/docs/overview)
* Since the returned data from Google is very limited, we next attempt to enrich the category (i.e. genre, subject, tags, etc.) with more data from [OpenLibrary](https://openlibrary.org/)
* Create a combined list of all the available categories and clean the text to be consistent, then count the frequency of each category occurrence across all the results to sort by relevance
* Use this list to query the Google Books API again and get a set of books for each category
* Create a final list by ranking the returned books by the number of matching categories to those that the searched book had
