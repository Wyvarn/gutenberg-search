from flask import current_app


def add_to_index(index, model):
    """
    Adds a model to the search index
    :param index: index name
    :param model: model
    """

    if not current_app.elasticsearch:
        return

    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)

    current_app.elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload)


def reset_index(index, model):
    """
    Resets the index
    :param index Index to reset
    :param model Model to add to index after reset
    :type index str
    """
    if not current_app.elasticsearch:
        return

    if current_app.elasticsearch.exists(index=index, doc_type=index, id=model.id):
        current_app.elastcisearch.delete(index=index, doc_type=index, id=model.id)

    # create the index
    current_app.elasticsearch.create(index=index, doc_type=index)
    add_to_index(index, model)


def remove_from_index(index, model):
    """
    Removes the model from the index
    :param index: index name
    :param model: Model
    """
    if not current_app.elasticsearch:
        return

    current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page=0, per_page=10):
    """
    Queries the index
    :param index: index name
    :param query: search query
    :param page: Page of the query
    :param per_page: results per page
    :return:
    """
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index=index, doc_type="book",
        body={
            "query": {
                "multi_match": {
                    "query": query,
                },
                # "from": (page - 1) * per_page,
                # "size": per_page
            }
        }
    )

    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total'], search["hits"]["hits"]
