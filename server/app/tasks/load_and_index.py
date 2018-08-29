from app import celery
from flask import current_app
from elasticsearch.exceptions import ConnectionError
from celery.utils.log import get_task_logger
import os
from app.mod_search.search import reset_index
from app.mod_search.models import Book


logger = get_task_logger(__name__)


@celery.task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True)
def load_and_index_es(self, index):

    # check if elasticsearch is available
    if not current_app.elasticsearch:
        logger.error('Elasticsearch not configured')
        return

    status = current_app.elasticsearch.indices.exists(index)

    if status:
        logger.info(f'Found index {index} loading data...')
        load_data_in_es.apply_async(index)
    else:
        logger.error(f'Index {index} not found')


@celery.task()
def load_data_in_es(self, index):
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
        logger.info(f"Reading books from directory {books_dir}")

        reset_index(index, Book)

        # read books directory
        for book in os.listdir(books_dir):
            logger.info(f"Reading file {book}")
            file_path = os.path.abspath(f"{books_dir}/{book}")

            # parse the book file
            title, author, paragraphs = parse_book_file(file_path)


