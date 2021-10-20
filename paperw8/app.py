from paperw8.configuration.config import DevelopmentConfig

from flask import Flask

import os
import sys

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevelopmentConfig())
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        # already exists
        pass
    
    # override config with env_variable_config
    app.config.from_envvar('PAPERW8_SETTINGS')

    # import db commands & functionality
    from paperw8.database import db
    db.init_app(app)

    # import login module
    from paperw8.user import auth
    app.register_blueprint(auth.bp)
    
    # import admin module
    from paperw8.data_processing import admin
    app.register_blueprint(admin.bp)
    
    # import chart module and set as home
    from paperw8.data_processing import performance
    app.register_blueprint(performance.bp)
    app.add_url_rule('/', endpoint='performance')
    
    # import blog module
    from paperw8.blog import blog
    app.register_blueprint(blog.bp)
    
    # import user module
    from paperw8.user import user
    app.register_blueprint(user.bp)
    
    # import contact module
    from paperw8.contact import contact
    app.register_blueprint(contact.bp)
    
    # import disclaimer module
    from paperw8.disclaimer import disclaimer
    app.register_blueprint(disclaimer.bp)

    return app