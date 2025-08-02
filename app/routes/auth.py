from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from app.utils.google_oauth import GoogleOAuth
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user with email and password."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/auth/google', methods=['GET'])
def google_login():
    """Initiate Google OAuth login."""
    try:
        authorization_url = GoogleOAuth.get_authorization_url()
        return jsonify({'authorization_url': authorization_url}), 200
    except Exception as e:
        current_app.logger.error(f"Google OAuth initiation error: {str(e)}")
        return jsonify({'error': 'Failed to initiate Google login'}), 500

@auth_bp.route('/auth/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback."""
    try:
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            return jsonify({'error': f'Google OAuth error: {error}'}), 400
        
        if not code:
            return jsonify({'error': 'Authorization code not provided'}), 400
        
        # Exchange code for token
        token_data = GoogleOAuth.exchange_code_for_token(code)
        if not token_data:
            return jsonify({'error': 'Failed to exchange code for token'}), 400
        
        # Get user info
        access_token = token_data.get('access_token')
        user_info = GoogleOAuth.get_user_info(access_token)
        
        if not user_info:
            return jsonify({'error': 'Failed to get user information'}), 400
        
        google_id = user_info.get('id')
        email = user_info.get('email')
        
        if not google_id or not email:
            return jsonify({'error': 'Incomplete user information from Google'}), 400
        
        # Check if user exists by Google ID
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Check if user exists by email
            user = User.query.filter_by(email=email.lower()).first()
            if user:
                # Link Google account to existing user
                user.google_id = google_id
            else:
                # Create new user
                user = User(email=email.lower(), google_id=google_id)
                db.session.add(user)
        
        db.session.commit()
        
        # Create access token
        jwt_token = create_access_token(identity=str(user.id))
        
        # Redirect to frontend with token (you might want to handle this differently)
        frontend_url = f"http://localhost:3001/auth/callback?token={jwt_token}"
        return redirect(frontend_url)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Google callback error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/auth/google-verify', methods=['POST'])
def google_verify():
    """Verify Google credential and login/register user."""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        data = request.get_json()
        if not data or 'credential' not in data:
            return jsonify({'error': 'Google credential is required'}), 400
        
        credential = data['credential']
        current_app.logger.info(f"Attempting Google token verification")
        
        # Verify the Google ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                credential, 
                requests.Request(), 
                current_app.config['GOOGLE_CLIENT_ID']
            )
            
            current_app.logger.info(f"Token verification successful for email: {idinfo.get('email')}")
            
            # Check if the token issuer is Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                current_app.logger.error(f"Invalid issuer: {idinfo['iss']}")
                raise ValueError('Wrong issuer.')
                
        except ValueError as e:
            current_app.logger.error(f"Token verification failed: {str(e)}")
            return jsonify({'error': f'Invalid Google token: {str(e)}'}), 400
        except Exception as e:
            current_app.logger.error(f"Unexpected token verification error: {str(e)}")
            return jsonify({'error': 'Token verification failed'}), 400
        
        # Extract user information
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')
        
        current_app.logger.info(f"Processing login for email: {email}")
        
        # Check if user exists
        user = User.query.filter_by(email=email.lower()).first()
        
        if not user:
            # Create new user
            current_app.logger.info(f"Creating new user for email: {email}")
            user = User(email=email.lower(), google_id=google_id)
            db.session.add(user)
        else:
            # Update Google ID if not set
            current_app.logger.info(f"Existing user found for email: {email}")
            if not user.google_id:
                user.google_id = google_id
        
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        current_app.logger.info(f"Login successful for user ID: {user.id}")
        
        return jsonify({
            'message': 'Google login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Google verify error: {str(e)}")
        return jsonify({'error': 'Google authentication failed'}), 500
