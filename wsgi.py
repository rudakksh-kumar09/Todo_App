"""
WSGI entry point for Render deployment.
This file provides an alternative entry point if needed.
"""

from run import app

if __name__ == "__main__":
    app.run()
