from flask import Flask, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Configure CORS
    CORS(app, 
         origins=app.config['CORS_ORIGINS'], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.todos import todos_bp
    
    # Import models to register them with SQLAlchemy
    from app.models import User, Todo
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(todos_bp, url_prefix='/api')
    
    # Add a simple health check endpoint
    @app.route('/')
    def health_check():
        return jsonify({'message': 'Todo API is running!', 'status': 'healthy'})
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'message': 'Todo API v1.0',
            'endpoints': [
                '/api/register',
                '/api/login',
                '/api/google-auth',
                '/api/todos'
            ]
        })
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        current_app.logger.error(f"Expired token: {jwt_header}, {jwt_payload}")
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        current_app.logger.error(f"Invalid token error: {error}")
        return jsonify({'error': 'Invalid token'}), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        current_app.logger.error(f"Missing token error: {error}")
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Log the error but don't fail the app creation
            print(f"Warning: Database tables creation skipped: {str(e)}")
    
    return app

# Create a module-level app instance for gunicorn app:app
app = create_app()
