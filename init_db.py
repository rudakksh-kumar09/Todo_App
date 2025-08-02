#!/usr/bin/env python3
"""
Database initialization script for TodoApp.
This script creates the database tables and can be used to set up the database.
"""

from app import create_app, db
from app.models import User, Todo

def init_db():
    """Initialize the database with tables."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Print table information
        print(f"Tables created: {db.metadata.tables.keys()}")

def reset_db():
    """Reset the database by dropping and recreating all tables."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped!")
        
        # Create all tables
        db.create_all()
        print("Database tables recreated successfully!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_db()
    else:
        init_db()
