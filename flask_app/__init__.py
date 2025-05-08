# 3rd-party packages
from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename


# stdlib
from datetime import datetime
import os

# local
from .client import BookClient

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

def custom_404(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from .users.routes import users
    from .books.routes import books

    app.register_blueprint(users)
    app.register_blueprint(books)
    app.register_error_handler(404, custom_404)

    login_manager.login_view = "users.login"


    return app

