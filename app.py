from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://wrestling_app:SLHSWrestling2025!@localhost/slhs_wrestling')

# Obscure admin login route - change this to something unpredictable
ADMIN_LOGIN_ROUTE = os.environ.get('ADMIN_LOGIN_ROUTE', 'cavaliers-wrestling-admin-portal-2025')

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        conn = psycopg2.connect(
            app.config['DATABASE_URL'],
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('admin_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Public Routes
@app.route('/')
def home():
    """Home page route - Southern Lee Wrestling"""
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    """About page route - Learn about Southern Lee Wrestling program"""
    return render_template('about.html', title='About')

@app.route('/team')
def team():
    """Team page route - Meet the Cavaliers wrestlers and coaches"""
    return render_template('team.html', title='Our Team')

@app.route('/schedule')
def schedule():
    """Schedule page route - Wrestling matches and tournament schedule"""
    return render_template('schedule.html', title='Schedule')

@app.route('/contact')
def contact():
    """Contact page route - Get in touch with Southern Lee Wrestling"""
    return render_template('contact.html', title='Contact')

# Admin Authentication Routes
@app.route(f'/{ADMIN_LOGIN_ROUTE}', methods=['GET', 'POST'])
def admin_login():
    """Secure admin login route with obscure URL"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('admin/login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'error')
            return render_template('admin/login.html')
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, password_hash, first_name, last_name, role, active
                FROM users 
                WHERE email = %s AND active = TRUE
            """, (email,))
            
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Update last login
                cursor.execute("""
                    UPDATE users 
                    SET last_login_at = %s, modified_at = %s 
                    WHERE id = %s
                """, (datetime.utcnow(), datetime.utcnow(), user['id']))
                conn.commit()
                
                # Set session
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                session['user_name'] = f"{user['first_name']} {user['last_name']}"
                session['user_role'] = user['role']
                
                flash(f'Welcome back, {user["first_name"]}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
        except psycopg2.Error as e:
            flash('Database error. Please try again.', 'error')
            print(f"Login error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout route"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard - requires login"""
    return render_template('admin/dashboard.html', title='Admin Dashboard')

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    """Change password - requires login"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('admin/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('admin/change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return render_template('admin/change_password.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error.', 'error')
            return render_template('admin/change_password.html')
        
        try:
            cursor = conn.cursor()
            # Get current user's password hash
            cursor.execute("""
                SELECT password_hash FROM users WHERE id = %s
            """, (session['user_id'],))
            
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user['password_hash'], current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('admin/change_password.html')
            
            # Update password
            new_password_hash = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, modified_at = %s 
                WHERE id = %s
            """, (new_password_hash, datetime.utcnow(), session['user_id']))
            conn.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except psycopg2.Error as e:
            flash('Database error. Please try again.', 'error')
            print(f"Password change error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin/change_password.html', title='Change Password')

@app.route('/admin/users')
@login_required
@role_required(['admin'])
def admin_users():
    """User management - admin only"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, first_name, last_name, role, created_at, last_login_at, active
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        return render_template('admin/users.html', users=users, title='User Management')
    except psycopg2.Error as e:
        flash('Error loading users.', 'error')
        print(f"Users error: {e}")
        return redirect(url_for('admin_dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_create_user():
    """Create new user - admin only"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        
        if not all([email, password, first_name, last_name, role]):
            flash('All fields are required.', 'error')
            return render_template('admin/create_user.html')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error.', 'error')
            return render_template('admin/create_user.html')
        
        try:
            cursor = conn.cursor()
            password_hash = generate_password_hash(password)
            
            cursor.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, password_hash, first_name, last_name, role))
            conn.commit()
            
            flash(f'User {email} created successfully!', 'success')
            return redirect(url_for('admin_users'))
            
        except psycopg2.IntegrityError:
            flash('Email address already exists.', 'error')
        except psycopg2.Error as e:
            flash('Error creating user.', 'error')
            print(f"Create user error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin/create_user.html', title='Create User')

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_edit_user(user_id):
    """Edit user - admin only"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            email = request.form.get('email')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            role = request.form.get('role')
            
            if not all([email, first_name, last_name, role]):
                flash('All fields are required.', 'error')
                return redirect(url_for('admin_edit_user', user_id=user_id))
            
            cursor.execute("""
                UPDATE users 
                SET email = %s, first_name = %s, last_name = %s, role = %s, modified_at = %s
                WHERE id = %s
            """, (email, first_name, last_name, role, datetime.utcnow(), user_id))
            conn.commit()
            
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_users'))
        
        # GET request - show form
        cursor.execute("""
            SELECT id, email, first_name, last_name, role, active
            FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_users'))
        
        return render_template('admin/edit_user.html', user=user, title='Edit User')
        
    except psycopg2.Error as e:
        flash('Database error.', 'error')
        print(f"Edit user error: {e}")
        return redirect(url_for('admin_users'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def admin_reset_password(user_id):
    """Reset user password - admin only"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not new_password or not confirm_password:
                flash('Both password fields are required.', 'error')
                return redirect(url_for('admin_reset_password', user_id=user_id))
            
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('admin_reset_password', user_id=user_id))
            
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return redirect(url_for('admin_reset_password', user_id=user_id))
            
            # Update password
            password_hash = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, modified_at = %s 
                WHERE id = %s
            """, (password_hash, datetime.utcnow(), user_id))
            conn.commit()
            
            flash('Password reset successfully!', 'success')
            return redirect(url_for('admin_users'))
        
        # GET request - show form
        cursor.execute("""
            SELECT id, email, first_name, last_name
            FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_users'))
        
        return render_template('admin/reset_password.html', user=user, title='Reset Password')
        
    except psycopg2.Error as e:
        flash('Database error.', 'error')
        print(f"Reset password error: {e}")
        return redirect(url_for('admin_users'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/toggle-user-status/<int:user_id>')
@login_required
@role_required(['admin'])
def admin_toggle_user_status(user_id):
    """Toggle user active status - admin only"""
    if user_id == session['user_id']:
        flash('You cannot change your own status.', 'error')
        return redirect(url_for('admin_users'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        cursor = conn.cursor()
        # Get current status
        cursor.execute("SELECT active, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_users'))
        
        # Toggle status
        new_status = not user['active']
        cursor.execute("""
            UPDATE users 
            SET active = %s, modified_at = %s 
            WHERE id = %s
        """, (new_status, datetime.utcnow(), user_id))
        conn.commit()
        
        status_text = "activated" if new_status else "deactivated"
        flash(f'User {user["email"]} has been {status_text}.', 'success')
        
    except psycopg2.Error as e:
        flash('Error updating user status.', 'error')
        print(f"Toggle status error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/delete-user/<int:user_id>')
@login_required
@role_required(['admin'])
def admin_delete_user(user_id):
    """Delete user - admin only"""
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        cursor = conn.cursor()
        # Get user info before deleting
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_users'))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        
        flash(f'User {user["email"]} has been deleted.', 'success')
        
    except psycopg2.Error as e:
        flash('Error deleting user.', 'error')
        print(f"Delete user error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    # Development server settings
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    # Use 0.0.0.0 to bind to all interfaces (accessible from internet when deployed)
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print("🤼 Starting Southern Lee Wrestling website...")
    print(f"📱 Server running on: http://{host}:{port}")
    print(f"🔐 Admin login: http://{host}:{port}/{ADMIN_LOGIN_ROUTE}")
    print("⚔️ Find A Way! - Cavaliers Wrestling")
    app.run(debug=debug_mode, host=host, port=port)