import os
from gbpartners.configuration.config import DevelopmentConfig

from flask import Flask
from flask_pagedown import PageDown

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
    
    print(os.getcwd())
    import sys
    sys.stdout.flush()
    # override config with env_variable_config
    app.config.from_envvar('GBPARTNERS_SETTINGS')

    # import db commands & functionality
    from gbpartners.database import db
    db.init_app(app)

    # import login module
    from gbpartners.user import auth
    app.register_blueprint(auth.bp)
    
    # import admin module
    from gbpartners.data_processing import admin
    app.register_blueprint(admin.bp)
    
    # import chart module and set as home
    from gbpartners.data_processing import performance
    app.register_blueprint(performance.bp)
    app.add_url_rule('/', endpoint='performance')
    
    # load pagedown module for blog
    pagedown = PageDown(app)
    # import blog module
    from gbpartners.blog import blog
    app.register_blueprint(blog.bp)
    
    # import user module
    from gbpartners.user import user
    app.register_blueprint(user.bp)
    
    # import contact module
    from gbpartners.contact import contact
    app.register_blueprint(contact.bp)

    return app