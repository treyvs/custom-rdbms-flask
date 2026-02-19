"""
app.py
Flask Web Application - Task Manager with REST API
Demonstrates CRUD operations and mobile API integration
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from functools import wraps
from rdbms.engine import Database, Column, DataType
from rdbms.storage import StorageManager
from rdbms.auth import hash_password, verify_password, create_token, verify_token

app = Flask(__name__)

storage = StorageManager("./task_manager_db")
db = Database(storage)


def init_database():
    """Initialize database tables"""
    if 'users' not in db.tables:
        db.create_table('users', [
            Column('id', DataType.INTEGER, nullable=False, primary_key=True, auto_increment=True),
            Column('username', DataType.TEXT, nullable=False, unique=True),
            Column('email', DataType.TEXT, nullable=False, unique=True),
            Column('password', DataType.TEXT, nullable=False),
            Column('created_at', DataType.DATETIME, nullable=False)
        ])
        print("✓ Users table created")

    if 'tasks' not in db.tables:
        db.create_table('tasks', [
            Column('id', DataType.INTEGER, nullable=False, primary_key=True, auto_increment=True),
            Column('user_id', DataType.INTEGER, nullable=False),
            Column('title', DataType.TEXT, nullable=False),
            Column('description', DataType.TEXT, nullable=True),
            Column('status', DataType.TEXT, nullable=False),
            Column('priority', DataType.INTEGER, nullable=False),
            Column('created_at', DataType.DATETIME, nullable=False),
            Column('updated_at', DataType.DATETIME, nullable=False)
        ])
        print("✓ Tasks table created")


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        kwargs['user_id'] = payload['user_id']
        kwargs['username'] = payload['username']
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    """Web UI home page"""
    try:
        users = db.select('users', order_by='-id')
        tasks = db.select('tasks', order_by='-id')
        return render_template('index.html', users=users, tasks=tasks)
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"


@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        existing = db.select('users', where={'username': username})
        if existing:
            return jsonify({'error': 'Username already exists'}), 409

        db.insert('users', {
            'username': username,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat()
        })

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400

        users = db.select('users', where={'username': username})
        if not users or not verify_password(password, users[0]['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        user = users[0]
        token = create_token(user['id'], user['username'])

        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['GET'])
@token_required
def api_get_tasks(user_id, username):
    """Get all tasks for authenticated user"""
    try:
        tasks = db.select('tasks', where={'user_id': user_id}, order_by='-id')
        return jsonify({'tasks': tasks}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['POST'])
@token_required
def api_create_task(user_id, username):
    """Create new task for authenticated user"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        priority = data.get('priority', 1)

        if not title:
            return jsonify({'error': 'Title is required'}), 400

        task = db.insert('tasks', {
            'user_id': user_id,
            'title': title,
            'description': description,
            'status': 'pending',
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })

        return jsonify({'task': task}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def api_update_task(task_id, user_id, username):
    """Update a task"""
    try:
        tasks = db.select('tasks', where={'id': task_id})
        if not tasks:
            return jsonify({'error': 'Task not found'}), 404

        if tasks[0]['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        update_data = {
            'updated_at': datetime.now().isoformat()
        }
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'priority' in data:
            update_data['priority'] = data['priority']

        db.update('tasks', update_data, {'id': task_id})
        updated_tasks = db.select('tasks', where={'id': task_id})

        return jsonify({'task': updated_tasks[0]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def api_delete_task(task_id, user_id, username):
    """Delete a task"""
    try:
        tasks = db.select('tasks', where={'id': task_id})
        if not tasks:
            return jsonify({'error': 'Task not found'}), 404

        if tasks[0]['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        db.delete('tasks', {'id': task_id})
        return jsonify({'message': 'Task deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    try:
        users = db.select('users')
        tasks = db.select('tasks')

        return jsonify({
            'total_users': len(users),
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t['status'] == 'completed']),
            'pending_tasks': len([t for t in tasks if t['status'] == 'pending']),
            'in_progress_tasks': len([t for t in tasks if t['status'] == 'in_progress'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_database()
    print("\n" + "=" * 60)
    print("TASK MANAGER - Web Application")
    print("=" * 60)
    print("Simple RDBMS Demonstration")
    print("Starting server at http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
