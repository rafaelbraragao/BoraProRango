import os

class Config:
    BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')  # valor padrão para desenvolvimento
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # ✅ Corrigido aqui
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    SECRET_KEY = os.getenv('SECRET_KEY', 'e1140a8d3ef3d8fc3fb2216b27112c1bf95c14efbb8f8f4ea98085f131b38213')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    TESTING = True
    MAIL_SUPPRESS_SEND = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False