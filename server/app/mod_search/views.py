from . import search
from flask import jsonify, request
from .search_wrapper import query_index
from elasticsearch.exceptions import RequestError


@search.route("/search", methods=["GET"])
def search_index():
    term = request.args.get("term")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    try:
        ids, result = query_index("library", term, page, per_page)
        return jsonify(dict(ids=ids, result=result)), 200
    except RequestError:
        return jsonify(dict(ids=[], result=[])), 400


