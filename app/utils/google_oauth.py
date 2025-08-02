import requests
from flask import current_app, url_for
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import json

class GoogleOAuth:
    """Google OAuth2 helper class."""
    
    @staticmethod
    def get_authorization_url():
        """Get the Google OAuth authorization URL."""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": current_app.config['GOOGLE_CLIENT_ID'],
            "redirect_uri": url_for('auth.google_callback', _external=True),
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{base_url}?{query_string}"
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for access token."""
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": current_app.config['GOOGLE_CLIENT_ID'],
            "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": url_for('auth.google_callback', _external=True)
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error exchanging code for token: {str(e)}")
            return None
    
    @staticmethod
    def get_user_info(access_token):
        """Get user information from Google API."""
        user_info_url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
        
        try:
            response = requests.get(user_info_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Error getting user info: {str(e)}")
            return None
    
    @staticmethod
    def verify_id_token(id_token_str):
        """Verify Google ID token."""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                current_app.config['GOOGLE_CLIENT_ID']
            )
            
            # Additional verification
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
        except ValueError as e:
            current_app.logger.error(f"Error verifying ID token: {str(e)}")
            return None
