import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'not-so-secret')
    DEBUG = False
    API_KEY = os.getenv('API_KEY', 'secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USERNAME", None)}:{os.getenv("DB_PASSWORD", None)}@{os.getenv("DB_HOST", None)}/{os.getenv("DB_DATABASE", None)}'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USERNAME", None)}:{os.getenv("DB_PASSWORD", None)}@{os.getenv("DB_HOST", None)}/{os.getenv("DB_DATABASE", None)}'


configurations = dict(dev=DevelopmentConfig, prod=ProductionConfig)
secret = Config.SECRET_KEY
