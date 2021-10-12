import os

from flask import Flask
from flask_pagedown import PageDown

from sqlite3 import OperationalError

import os

UPLOAD_FOLDER = os.path.join('gbpartners', 'static')
MAX_FILE_SIZE = 5 * 10**3 * 10**3

def create_app(test_config=None):
    # create and configure the app
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'gbpartners.sqlite'),
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        MAX_CONTENT_LENGTH=MAX_FILE_SIZE,
        STATIC_FOLDER='static'
    )

    app = Flask(__name__, instance_relative_config=True)
    pagedown = PageDown(app)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import admin
    app.register_blueprint(admin.bp)
    
    from . import performance
    app.register_blueprint(performance.bp)
    app.add_url_rule('/', endpoint='blog')
    
    from . import blog
    app.register_blueprint(blog.bp)
    
    from . import user
    app.register_blueprint(user.bp)
    
    from . import contact
    app.register_blueprint(contact.bp)

    return app