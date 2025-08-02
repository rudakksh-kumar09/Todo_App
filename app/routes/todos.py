from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Todo
from app.utils.email import send_todo_creation_email

todos_bp = Blueprint('todos', __name__)

def get_current_user_id():
    """Get current user ID as integer from JWT token."""
    return int(get_jwt_identity())

@todos_bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    """Get all todos for the current user."""
    try:
        current_user_id = get_current_user_id()
        
        # Get query parameters for filtering/sorting
        completed = request.args.get('completed')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        
        # Build query
        query = Todo.query.filter_by(user_id=current_user_id)
        
        # Filter by completion status if specified
        if completed is not None:
            is_completed = completed.lower() in ['true', '1', 'yes']
            query = query.filter_by(completed=is_completed)
        
        # Sort todos
        if sort_by in ['title', 'created_at', 'updated_at', 'completed']:
            if order.lower() == 'asc':
                query = query.order_by(getattr(Todo, sort_by).asc())
            else:
                query = query.order_by(getattr(Todo, sort_by).desc())
        
        todos = query.all()
        
        return jsonify({
            'todos': [todo.to_dict() for todo in todos],
            'count': len(todos)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get todos error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@todos_bp.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    """Create a new todo."""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        # Validate input
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        if len(title) > 200:
            return jsonify({'error': 'Title must be 200 characters or less'}), 400
        
        # Get user for email notification
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create new todo
        todo = Todo(
            title=title,
            description=description,
            user_id=current_user_id
        )
        
        db.session.add(todo)
        db.session.commit()
        
        # Send email notification
        try:
            send_todo_creation_email(user.email, title)
        except Exception as email_error:
            current_app.logger.error(f"Email sending error: {str(email_error)}")
            # Don't fail the request if email fails
        
        return jsonify({
            'message': 'Todo created successfully',
            'todo': todo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create todo error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@todos_bp.route('/todos/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    """Get a specific todo."""
    try:
        current_user_id = get_current_user_id()
        
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        return jsonify({'todo': todo.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Get todo error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@todos_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    """Update an existing todo."""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        # Update fields if provided
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'error': 'Title cannot be empty'}), 400
            if len(title) > 200:
                return jsonify({'error': 'Title must be 200 characters or less'}), 400
            todo.title = title
        
        if 'description' in data:
            todo.description = data['description'].strip()
        
        if 'completed' in data:
            if not isinstance(data['completed'], bool):
                return jsonify({'error': 'Completed must be a boolean value'}), 400
            todo.completed = data['completed']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Todo updated successfully',
            'todo': todo.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update todo error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@todos_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    """Delete a todo."""
    try:
        current_user_id = get_current_user_id()
        
        todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()
        
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify({'message': 'Todo deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete todo error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@todos_bp.route('/todos/bulk-update', methods=['PUT'])
@jwt_required()
def bulk_update_todos():
    """Bulk update todos (e.g., mark multiple as completed)."""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        todo_ids = data.get('todo_ids', [])
        updates = data.get('updates', {})
        
        if not todo_ids or not updates:
            return jsonify({'error': 'Todo IDs and updates are required'}), 400
        
        # Validate updates
        valid_fields = ['completed', 'title', 'description']
        for field in updates.keys():
            if field not in valid_fields:
                return jsonify({'error': f'Invalid field: {field}'}), 400
        
        # Update todos
        todos = Todo.query.filter(
            Todo.id.in_(todo_ids),
            Todo.user_id == current_user_id
        ).all()
        
        if not todos:
            return jsonify({'error': 'No todos found'}), 404
        
        updated_todos = []
        for todo in todos:
            if 'completed' in updates:
                todo.completed = updates['completed']
            if 'title' in updates and updates['title']:
                todo.title = updates['title']
            if 'description' in updates:
                todo.description = updates['description']
            updated_todos.append(todo.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(updated_todos)} todos updated successfully',
            'todos': updated_todos
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Bulk update todos error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@todos_bp.route('/todos/stats', methods=['GET'])
@jwt_required()
def get_todo_stats():
    """Get todo statistics for the current user."""
    try:
        current_user_id = get_current_user_id()
        
        total_todos = Todo.query.filter_by(user_id=current_user_id).count()
        completed_todos = Todo.query.filter_by(user_id=current_user_id, completed=True).count()
        pending_todos = total_todos - completed_todos
        
        completion_rate = (completed_todos / total_todos * 100) if total_todos > 0 else 0
        
        return jsonify({
            'total_todos': total_todos,
            'completed_todos': completed_todos,
            'pending_todos': pending_todos,
            'completion_rate': round(completion_rate, 2)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get todo stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
