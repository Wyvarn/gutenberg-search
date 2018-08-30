from app import celery
from flask import current_app
from elasticsearch.exceptions import ConnectionError
from celery.utils.log import get_task_logger
import os
import re
from app.mod_search.search import reset_index
from app.mod_search.models import Book


logger = get_task_logger(__name__)


@celery.task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True)
def load_and_index_es(self, index):

    if not current_app.elasticsearch:
        logger.error('Elasticsearch not configured')
        return

    status = current_app.elasticsearch.indices.exists(index)

    if not status:
        logger.warn(f'Index {index} not found, loading data')
        load_data_in_es(index)
    else:
        logger.info(f'Found index {index} in es')


def load_data_in_es(index):

    logger.info(f'Loading index {index} in ES')

    def parse_book_file(file_path):
        """
        Parses the book file
        :param file_path: File path to the book to parse
        :type file_path str
        :return: Returns a tuple with the title, author and paragraphs
        :rtype: tuple
        """
        title = ''
        author = ''
        paragraphs = []

        with open(file_path, mode="r") as file:
            for line in file:
                if re.match('^Title:\s(.+)$', line):
                    title = line

                if re.match('^Author:\s(.+)$', line):
                    author = line

                start_of_book_match = re.match('^\*{3}\s*START OF (THIS|THE) PROJECT GUTENBERG EBOOK.+\*{3}$', line)
                end_of_book_match = re.match('\*{3}\s*END OF (THIS|THE) PROJECT GUTENBERG EBOOK.+\*{3}$', line)

                if end_of_book_match:
                    break

                if not start_of_book_match or not len(line) == 0 or not line == '\n' or not line == '' \
                        or not end_of_book_match:
                    new_line = re.sub(r'[\r\n_]', '', line)

                    if new_line != '':
                        paragraphs.append(new_line)

        return title, 'Unknown Author' if len(author) == 0 else author, paragraphs

    def read_and_insert_books(books_dir="files/books"):
        """
        Reads and inserts books from the books directory
        :param books_dir Books directory
        """
        logger.info(f"Reading books from directory {books_dir}")

        # reset_index(index, Book)

        for book in os.listdir(books_dir):
            logger.info(f"Reading file {book}")
            file_path = os.path.abspath(f"{books_dir}/{book}")

            title, author, paragraphs = parse_book_file(file_path)
            insert_book_data(title, author, paragraphs)

    def insert_book_data(title, author, paragraphs):
        bulk_operations = []

        for x in range(len(paragraphs)):
            bulk_operations.append(dict(index={'_index': index, '_type': 'book'}))
            bulk_operations.append(dict(
                author=author,
                title=title,
                location=x,
                text=paragraphs[x]
            ))

            if x > 0 and  x % 500 == 0:
                current_app.elasticsearch.bulk({'index': index, 'body': bulk_operations})
                bulk_operations = []
                logger.info(f'Indexed Paragraphs {x - 499} - {x}')

        current_app.elasticsearch.bulk({'body': bulk_operations})
        logger.info(f'Indexed Paragraphs {len(paragraphs) - len(bulk_operations) / 2} - {len(paragraphs)}\n')

    read_and_insert_books()
