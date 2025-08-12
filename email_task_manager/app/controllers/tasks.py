"""
Tasks controller for managing tasks.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Task, User
from app.services.printer import print_task

# Create blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
@login_required
def index():
    """Display all tasks."""
    # Get filter parameters
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    assigned_to = request.args.get('assigned_to', 'all')
    
    # Build query
    query = Task.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if priority != 'all':
        query = query.filter_by(priority=priority)
    
    if assigned_to != 'all':
        if assigned_to == 'me':
            query = query.filter_by(assigned_to_id=current_user.id)
        elif assigned_to == 'unassigned':
            query = query.filter_by(assigned_to_id=None)
        else:
            try:
                user_id = int(assigned_to)
                query = query.filter_by(assigned_to_id=user_id)
            except ValueError:
                pass
    
    # Order by creation date (newest first)
    tasks = query.order_by(Task.created_at.desc()).all()
    
    # Get users for assignment dropdown
    users = User.query.all()
    
    return render_template(
        'tasks/index.html',
        tasks=tasks,
        users=users,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        statuses=current_app.config['TASK_STATUSES'],
        priorities=current_app.config['TASK_PRIORITIES']
    )

@tasks_bp.route('/<int:task_id>')
@login_required
def view(task_id):
    """View a specific task."""
    task = Task.query.get_or_404(task_id)
    return render_template('tasks/view.html', task=task)

@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new task."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        status = request.form.get('status', 'New')
        due_date_str = request.form.get('due_date')
        assigned_to_id = request.form.get('assigned_to_id')
        requestor_name = request.form.get('requestor_name')
        requestor_email = request.form.get('requestor_email')
        location = request.form.get('location')
        
        # Validate input
        if not title:
            flash('Title is required', 'error')
            return render_template('tasks/create.html')
        
        # Create new task
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status,
            requestor_name=requestor_name,
            requestor_email=requestor_email,
            location=location
        )
        
        # Set due date if provided
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid due date format', 'error')
                return render_template('tasks/create.html')
        
        # Set assigned user if provided
        if assigned_to_id:
            try:
                task.assigned_to_id = int(assigned_to_id)
            except ValueError:
                pass
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully', 'success')
        return redirect(url_for('tasks.view', task_id=task.id))
    
    # Get users for assignment dropdown
    users = User.query.all()
    
    return render_template(
        'tasks/create.html',
        users=users,
        statuses=current_app.config['TASK_STATUSES'],
        priorities=current_app.config['TASK_PRIORITIES']
    )

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """Edit a task."""
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority')
        task.status = request.form.get('status')
        task.requestor_name = request.form.get('requestor_name')
        task.requestor_email = request.form.get('requestor_email')
        task.location = request.form.get('location')
        
        # Set due date if provided
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid due date format', 'error')
                return render_template('tasks/edit.html', task=task)
        else:
            task.due_date = None
        
        # Set assigned user if provided
        assigned_to_id = request.form.get('assigned_to_id')
        if assigned_to_id:
            try:
                task.assigned_to_id = int(assigned_to_id)
            except ValueError:
                task.assigned_to_id = None
        else:
            task.assigned_to_id = None
        
        # Set completed date if status is Completed
        if task.status == 'Completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif task.status != 'Completed':
            task.completed_at = None
        
        db.session.commit()
        
        flash('Task updated successfully', 'success')
        return redirect(url_for('tasks.view', task_id=task.id))
    
    # Get users for assignment dropdown
    users = User.query.all()
    
    return render_template(
        'tasks/edit.html',
        task=task,
        users=users,
        statuses=current_app.config['TASK_STATUSES'],
        priorities=current_app.config['TASK_PRIORITIES']
    )

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully', 'success')
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/<int:task_id>/print', methods=['POST'])
@login_required
def print_task_route(task_id):
    """Print a task."""
    task = Task.query.get_or_404(task_id)
    
    try:
        success = print_task(task)
        
        if success:
            flash('Task printed successfully', 'success')
        else:
            flash('Failed to print task', 'error')
            
    except Exception as e:
        flash(f'Error printing task: {str(e)}', 'error')
    
    return redirect(url_for('tasks.view', task_id=task.id))

@tasks_bp.route('/<int:task_id>/status', methods=['POST'])
@login_required
def update_status(task_id):
    """Update task status."""
    task = Task.query.get_or_404(task_id)
    
    status = request.form.get('status')
    if status in current_app.config['TASK_STATUSES']:
        task.status = status
        
        # Set completed date if status is Completed
        if status == 'Completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif status != 'Completed':
            task.completed_at = None
            
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        
        flash('Task status updated', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
            
        flash('Invalid status', 'error')
    
    return redirect(url_for('tasks.view', task_id=task.id))

@tasks_bp.route('/<int:task_id>/assign', methods=['POST'])
@login_required
def assign_task(task_id):
    """Assign a task to a user."""
    task = Task.query.get_or_404(task_id)
    
    user_id = request.form.get('user_id')
    if user_id:
        try:
            user = User.query.get(int(user_id))
            if user:
                task.assigned_to_id = user.id
                db.session.commit()
                flash(f'Task assigned to {user.username}', 'success')
            else:
                flash('User not found', 'error')
        except ValueError:
            flash('Invalid user ID', 'error')
    else:
        # Unassign task
        task.assigned_to_id = None
        db.session.commit()
        flash('Task unassigned', 'success')
    
    return redirect(url_for('tasks.view', task_id=task.id))