import os 
from dotenv import load_dotenv 

load_dotenv() 
 
class Config: 
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'groq')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
class DevelopmentConfig(Config):
    DEBUG = True 
class ProductionConfig(Config):
    DEBUG = False 
config_by_name = { 
    'dev': DevelopmentConfig, 
    'prod': ProductionConfig, 
    'default': DevelopmentConfig 
    }
