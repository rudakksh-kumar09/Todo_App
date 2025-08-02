#!/usr/bin/env python3
"""
Simple test script for TodoApp API endpoints.
This script tests basic functionality of the API.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_register():
    """Test user registration."""
    print("Testing user registration...")
    
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=data)
    
    if response.status_code == 201:
        print("✓ Registration successful")
        return response.json().get('access_token')
    elif response.status_code == 409:
        print("! User already exists, trying login...")
        return test_login()
    else:
        print(f"✗ Registration failed: {response.text}")
        return None

def test_login():
    """Test user login."""
    print("Testing user login...")
    
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    
    if response.status_code == 200:
        print("✓ Login successful")
        return response.json().get('access_token')
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_create_todo(token):
    """Test todo creation."""
    print("Testing todo creation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Todo",
        "description": "This is a test todo item"
    }
    
    response = requests.post(f"{BASE_URL}/todos", json=data, headers=headers)
    
    if response.status_code == 201:
        print("✓ Todo creation successful")
        return response.json().get('todo', {}).get('id')
    else:
        print(f"✗ Todo creation failed: {response.text}")
        return None

def test_get_todos(token):
    """Test getting todos."""
    print("Testing get todos...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/todos", headers=headers)
    
    if response.status_code == 200:
        todos = response.json().get('todos', [])
        print(f"✓ Got {len(todos)} todos")
        return todos
    else:
        print(f"✗ Get todos failed: {response.text}")
        return []

def test_update_todo(token, todo_id):
    """Test todo update."""
    if not todo_id:
        print("! No todo ID to update")
        return
    
    print(f"Testing todo update for ID {todo_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Updated Test Todo",
        "completed": True
    }
    
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=data, headers=headers)
    
    if response.status_code == 200:
        print("✓ Todo update successful")
    else:
        print(f"✗ Todo update failed: {response.text}")

def test_delete_todo(token, todo_id):
    """Test todo deletion."""
    if not todo_id:
        print("! No todo ID to delete")
        return
    
    print(f"Testing todo deletion for ID {todo_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}", headers=headers)
    
    if response.status_code == 200:
        print("✓ Todo deletion successful")
    else:
        print(f"✗ Todo deletion failed: {response.text}")

def test_get_stats(token):
    """Test getting todo statistics."""
    print("Testing todo statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/todos/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Stats: {stats}")
    else:
        print(f"✗ Get stats failed: {response.text}")

def main():
    """Run all tests."""
    print("Starting TodoApp API Tests")
    print("=" * 50)
    
    try:
        # Test authentication
        token = test_register()
        if not token:
            print("Failed to get authentication token. Exiting.")
            sys.exit(1)
        
        print()
        
        # Test todos
        todo_id = test_create_todo(token)
        print()
        
        todos = test_get_todos(token)
        print()
        
        if not todo_id and todos:
            todo_id = todos[0].get('id')
        
        test_update_todo(token, todo_id)
        print()
        
        test_get_stats(token)
        print()
        
        test_delete_todo(token, todo_id)
        print()
        
        print("=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to the API. Make sure the server is running on localhost:5000")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
