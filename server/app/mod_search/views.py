from . import search
from flask import jsonify


@search.route("/health", methods=["GET"])
def health():
    return jsonify(dict(message="OK")), 200

