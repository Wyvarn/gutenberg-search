from flask import Blueprint

search = Blueprint(import_name=__name__, static_folder="static", template_folder="templates", url_prefix="/api/search",
                   name="search")

from . import views
