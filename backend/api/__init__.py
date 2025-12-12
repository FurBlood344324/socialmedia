from flask import Flask
from flask_cors import CORS
from api.config import Config
from api.extensions import db
from sqlalchemy import text
import os


def init_database(app):
    """Initialize database with init.sql script"""
    init_sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init.sql')
    
    if not os.path.exists(init_sql_path):
        print("⚠️  init.sql not found, skipping database initialization")
        return
    
    with app.app_context():
        try:
            # Check if tables already exist
            result = db.session.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            ))
            tables_exist = result.scalar()
            
            if tables_exist:
                print("✅ Database tables already exist, skipping initialization")
                return
            
            # Read and execute init.sql
            with open(init_sql_path, 'r') as f:
                sql_script = f.read()
            
            # Execute the script
            db.session.execute(text(sql_script))
            db.session.commit()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database initialization error: {e}")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS with explicit settings for local development
    CORS(app, 
         resources={r"/api/*": {
             "origins": Config.CORS_ORIGINS,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})
    
    # Initialize database
    db.init_app(app)
    
    # Initialize database schema
    init_database(app)
    
    # Register blueprints (import here to avoid circular imports)
    from api.controllers.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app