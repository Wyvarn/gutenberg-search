from app import app_logger
from flask import current_app
from app.mod_search.search import reset_index
from app.mod_search.models import Book
import os


def parse_book_file(file_path):
    """
    Parses the book file
    :param file_path: File path to the book to parse
    :type file_path str
    :return: Returns a tuple with the title, author and paragraphs
    :rtype: tuple
    """

    # read text file
    with open(file_path) as file:
        print(file)



def read_and_insert_books(books_dir="files/books"):
    """
    Reads and inserts books from the books directory
    :param books_dir Books directory
    """
    app_logger.info(f"Reading books from directory {books_dir}")

    if not current_app.elasticsearch:
        app_logger.error(f"Elasticsearch unavailable")
        return

    reset_index("library", Book)

    # read books directory
    for book in os.listdir(books_dir):
        app_logger.info(f"Reading file {book}")
        file_path = os.path.abspath(f"{books_dir}/{book}")

        # parse the book file
        title, author, paragraphs = parse_book_file(file_path)

