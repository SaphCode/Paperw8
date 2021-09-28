'''
import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = "9asdf8980as3459jkds79346ds4f3435fa64ˆGggd76HSD57hsˆSDnb" # TODO change this
    
class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
    SECRET_KEY = "secret_for_test_environment"
'''