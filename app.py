"""
app.py
Flask Web Application - Task Manager Demo
Demonstrates CRUD operations with the Simple RDBMS
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from rdbms.engine import Database, Column, DataType
from rdbms.storage import StorageManager

app = Flask(__name__)

# Initialize database
storage = StorageManager("./task_manager_db")
db = Database(storage)


def init_database():
    """Initialize database tables"""
    # Create users table
    if 'users' not in db.tables:
        db.create_table('users', [
            Column('id', DataType.INTEGER, nullable=False, primary_key=True, auto_increment=True),
            Column('username', DataType.TEXT, nullable=False, unique=True),
            Column('email', DataType.TEXT, nullable=False, unique=True),
            Column('created_at', DataType.DATETIME, nullable=False)
        ])
        print("✓ Users table created")
    
    # Create tasks table
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


@app.route('/')
def index():
    """Home page with users and tasks"""
    try:
        users = db.select('users', order_by='-id')
        tasks = db.select('tasks', order_by='-id')
        
        # Calculate statistics
        stats = {
            'total_users': len(users),
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t['status'] == 'completed']),
            'pending_tasks': len([t for t in tasks if t['status'] == 'pending']),
            'in_progress_tasks': len([t for t in tasks if t['status'] == 'in_progress'])
        }
        
        message = request.args.get('message')
        message_type = request.args.get('type', 'success')
        
        return render_template('index.html', 
                             users=users, 
                             tasks=tasks, 
                             stats=stats,
                             message=message,
                             message_type=message_type)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/users/create', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        username = request.form['username']
        email = request.form['email']
        
        db.insert('users', {
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat()
        })
        
        return redirect(url_for('index', message=f'User "{username}" created!', type='success'))
    except Exception as e:
        return redirect(url_for('index', message=f'Error: {str(e)}', type='error'))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user and all their tasks"""
    try:
        # Get user info before deleting
        users = db.select('users', where={'id': user_id})
        username = users[0]['username'] if users else 'Unknown'
        
        # Delete all tasks for this user
        task_count = db.delete('tasks', {'user_id': user_id})
        
        # Delete the user
        db.delete('users', {'id': user_id})
        
        return redirect(url_for('index', 
                               message=f'User "{username}" and {task_count} task(s) deleted!', 
                               type='success'))
    except Exception as e:
        return redirect(url_for('index', message=f'Error: {str(e)}', type='error'))


@app.route('/tasks/create', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        user_id = int(request.form['user_id'])
        title = request.form['title']
        description = request.form.get('description', '')
        priority = int(request.form['priority'])
        
        db.insert('tasks', {
            'user_id': user_id,
            'title': title,
            'description': description,
            'status': 'pending',
            'priority': priority,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        })
        
        return redirect(url_for('index', message=f'Task "{title}" created!', type='success'))
    except Exception as e:
        return redirect(url_for('index', message=f'Error: {str(e)}', type='error'))


@app.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task(task_id):
    """Update task status"""
    try:
        status = request.form['status']
        
        db.update('tasks', 
                 {'status': status, 'updated_at': datetime.now().isoformat()},
                 {'id': task_id})
        
        return redirect(url_for('index', message='Task status updated!', type='success'))
    except Exception as e:
        return redirect(url_for('index', message=f'Error: {str(e)}', type='error'))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    try:
        # Get task info before deleting
        tasks = db.select('tasks', where={'id': task_id})
        title = tasks[0]['title'] if tasks else 'Unknown'
        
        db.delete('tasks', {'id': task_id})
        
        return redirect(url_for('index', message=f'Task "{title}" deleted!', type='success'))
    except Exception as e:
        return redirect(url_for('index', message=f'Error: {str(e)}', type='error'))


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
    print("\n" + "="*60)
    print("TASK MANAGER - Web Application")
    print("="*60)
    print("Simple RDBMS Demonstration")
    print("Starting server at http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)