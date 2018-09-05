from flask import Blueprint

search = Blueprint(name="search", import_name=__name__, url_prefix="/api/search", static_folder="static",
                   template_folder="templates")

from . import views
