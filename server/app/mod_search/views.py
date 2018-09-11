from . import search
from flask import jsonify, request
from .search_wrapper import query_index, index_exists
from elasticsearch.exceptions import RequestError
from app import app_logger


@search.route("/search", methods=["GET"])
def search_index():
    term = request.args.get("term", type=str)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if index_exists():
        try:
            search_result = query_index("library", term, page, per_page)
            return jsonify(dict(ids=search_result.get("ids", []),
                                total=search_result.get("total", 0),
                                index=search_result.get("index", "library"),
                                results=search_result.get("results", []))
                           ), 200
        except RequestError as re:
            app_logger.error(f"Request failed with {re}")
            return jsonify(dict(ids=[], total=0, index="library", results=[])), 400
    else:
        return jsonify(dict(message="Index does not exist", results=[])), 404
