import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    UPLOAD_FOLDER = os.path.join('gbpartners', 'static')
    MAX_FILE_SIZE = 3 * 10**3 * 10**3
    STATIC_FOLDER = 'static'
    
class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = "dev"
    INSTANCE_PATH='instance'
    DATABASE=os.path.join(INSTANCE_PATH, 'gbpartners.sqlite')