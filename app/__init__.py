from dotenv import load_dotenv
import os
from app.extensions import db, jwt, migrate
from flask_cors import CORS
from flask import Flask
from app.models import Oferta, Busqueda, Nota


load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    env = os.getenv('FLASK_ENV','development').capitalize() + 'Config'
    app.config.from_object(f'app.config.config.{env}')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @app.route('/')
    def index():
        return "BIENVENIDO A POLIMONIACO"
    
    return app