from flask import Blueprint

# The 'templates' folder under this package contains the blueprint's templates.
# Keeping it explicit clarifies that index.html and other views live here.
main_bp = Blueprint('main', __name__, template_folder='templates')

from app.main import routes
