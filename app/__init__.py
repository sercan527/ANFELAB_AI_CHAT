from flask import Flask
from flask_cors import CORS
from config import Config
from app.database import init_db, close_db

def create_app():
    """Uygulama Fabrikası (Application Factory)"""
    app = Flask(__name__)
    

    app.config.from_object(Config)
    

    if not app.config.get('DATABASE_URL'):
        app.config['DATABASE_URL'] = 'sqlite:///app.db'
        

    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    

    app.teardown_appcontext(close_db)
    

    from app.routes import main_bp
    app.register_blueprint(main_bp)
    

    init_db(app)
    
    return app