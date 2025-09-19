from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY=os.getenv('SECRET_KEY')
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_TRACKS_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI')

class DevelopmentConfig(Config):
    DEBUG=True

class ProductionConfig(Config):
    DEBUG=False
class TestingConfig(Config):
    TESTING=True