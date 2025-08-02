"""
Entry point for Render deployment.
This file creates the Flask app instance that Gunicorn expects.
"""

from run import app

# This is what gunicorn app:app will look for
if __name__ == "__main__":
    app.run()
