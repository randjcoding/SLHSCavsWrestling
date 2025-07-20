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
app = Flask(__name__, static_folder='static')

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

@app.route('/roster')
@app.route('/roster/<int:year_id>')
def roster(year_id=None):
    """Roster page route - Meet the Cavaliers wrestlers and coaches"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return render_template('roster.html', title='Wrestling Roster', staff=[], wrestlers=[], years=[], current_year='2025-2026')
    
    try:
        cursor = conn.cursor()
        
        # Get all years for year selection
        cursor.execute("SELECT * FROM years ORDER BY start_year DESC")
        years = cursor.fetchall()
        
        # Determine current year
        if year_id:
            current_year_id = year_id
            cursor.execute("SELECT school_year FROM years WHERE id = %s", (year_id,))
            current_year_result = cursor.fetchone()
            current_year = current_year_result['school_year'] if current_year_result else '2025-2026'
        else:
            cursor.execute("SELECT id, school_year FROM years WHERE is_current = TRUE LIMIT 1")
            current_year_result = cursor.fetchone()
            if current_year_result:
                current_year_id = current_year_result['id']
                current_year = current_year_result['school_year']
            else:
                current_year_id = None
                current_year = '2025-2026'
        
        # Get staff for the selected year
        cursor.execute("""
            SELECT s.id, s.first_name, s.last_name, s.role, s.email, s.phone_number,
                   sd.biography, sd.wrestling_history, sd.years_coaching, sd.achievements,
                   sd.show_in_modal, sd.certifications, sd.education, sd.specialties,
                   sp.photo_url as primary_photo_url
            FROM staff s
            LEFT JOIN staffDetails sd ON s.id = sd.staff_id
            LEFT JOIN staffPhotos sp ON s.id = sp.staff_id AND sp.photo_type = 'primary'
            WHERE s.active = TRUE AND (s.year_id = %s OR %s IS NULL)
            ORDER BY 
                CASE s.role 
                    WHEN 'head_coach' THEN 1
                    WHEN 'assistant_coach' THEN 2
                    WHEN 'manager' THEN 3
                    ELSE 4
                END,
                s.last_name, s.first_name
        """, (current_year_id, current_year_id))
        staff_raw = cursor.fetchall()
        
        # Process staff data to handle JSON fields and modal settings
        staff = []
        for staff_member in staff_raw:
            staff_dict = dict(staff_member)
            # Parse JSON fields
            if staff_dict.get('achievements'):
                staff_dict['achievements'] = staff_dict['achievements'] if isinstance(staff_dict['achievements'], list) else []
            else:
                staff_dict['achievements'] = []
            
            # Parse modal settings
            modal_settings = staff_dict.get('show_in_modal', {})
            if isinstance(modal_settings, dict):
                staff_dict['show_biography'] = modal_settings.get('biography', True)
                staff_dict['show_wrestling_history'] = modal_settings.get('wrestling_history', True)
                staff_dict['show_years_coaching'] = modal_settings.get('years_coaching', True)
                staff_dict['show_achievements'] = modal_settings.get('achievements', True)
            else:
                staff_dict['show_biography'] = True
                staff_dict['show_wrestling_history'] = True
                staff_dict['show_years_coaching'] = True
                staff_dict['show_achievements'] = True
            
            staff.append(staff_dict)
        
        # Get wrestlers for the selected year
        cursor.execute("""
            SELECT w.id, w.first_name, w.last_name, w.division, w.level, w.rank_in_division,
                   w.grade, w.email, w.wins, w.losses,
                   wc.name as weight_class_name, wc.max_weight,
                   wd.biography, wd.achievements, wd.collegiate_aspirations, wd.role,
                   wd.primary_photo_url, wd.secondary_photo_url, wd.show_in_modal,
                   wd.home_town, wd.home_state, wd.track_wrestling_url
            FROM wrestlers w
            LEFT JOIN weightClasses wc ON w.weight_class_id = wc.id
            LEFT JOIN wrestlerDetails wd ON w.id = wd.wrestler_id
            WHERE w.active = TRUE AND (w.year_id = %s OR %s IS NULL)
            ORDER BY w.division, w.level, wc.max_weight, w.rank_in_division
        """, (current_year_id, current_year_id))
        wrestlers_raw = cursor.fetchall()
        
        # Process wrestler data
        wrestlers = []
        for wrestler in wrestlers_raw:
            wrestler_dict = dict(wrestler)
            # Parse JSON fields
            if wrestler_dict.get('achievements'):
                wrestler_dict['achievements'] = wrestler_dict['achievements'] if isinstance(wrestler_dict['achievements'], list) else []
            else:
                wrestler_dict['achievements'] = []
            
            # Parse modal settings
            modal_settings = wrestler_dict.get('show_in_modal', {})
            if isinstance(modal_settings, dict):
                wrestler_dict['show_biography'] = modal_settings.get('biography', True)
                wrestler_dict['show_achievements'] = modal_settings.get('achievements', True)
                wrestler_dict['show_collegiate_aspirations'] = modal_settings.get('collegiate_aspirations', True)
                wrestler_dict['show_record'] = modal_settings.get('record', True)
            else:
                wrestler_dict['show_biography'] = True
                wrestler_dict['show_achievements'] = True
                wrestler_dict['show_collegiate_aspirations'] = True
                wrestler_dict['show_record'] = True
            
            wrestlers.append(wrestler_dict)
        
        return render_template('roster.html', title='Wrestling Roster', 
                             staff=staff, wrestlers=wrestlers, years=years,
                             current_year=current_year, current_year_id=current_year_id)
        
    except psycopg2.Error as e:
        flash('Error loading roster data.', 'error')
        print(f"Roster page error: {e}")
        return render_template('roster.html', title='Wrestling Roster', staff=[], wrestlers=[], years=[], current_year='2025-2026')
    finally:
        cursor.close()
        conn.close()

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

# =====================================================
# ROSTER MANAGEMENT ROUTES (Admin Protected)
# =====================================================

@app.route('/admin/roster')
@login_required
@role_required(['admin', 'coach'])
def admin_roster():
    """Roster management dashboard"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = conn.cursor()
        
        # Get current year stats
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM wrestlers w JOIN years y ON w.year_id = y.id WHERE y.is_current = TRUE AND w.active = TRUE) as total_wrestlers,
                (SELECT COUNT(*) FROM wrestlers w JOIN years y ON w.year_id = y.id WHERE y.is_current = TRUE AND w.level = 'Varsity' AND w.active = TRUE) as varsity_wrestlers,
                (SELECT COUNT(*) FROM wrestlers w JOIN years y ON w.year_id = y.id WHERE y.is_current = TRUE AND w.level = 'JV' AND w.active = TRUE) as jv_wrestlers,
                (SELECT COUNT(*) FROM staff s JOIN years y ON s.year_id = y.id WHERE y.is_current = TRUE AND s.active = TRUE) as total_staff
        """)
        stats = cursor.fetchone()
        
        # Get weight class distribution
        cursor.execute("""
            SELECT wc.name, wc.division, COUNT(w.id) as wrestler_count
            FROM weightClasses wc
            LEFT JOIN wrestlers w ON wc.id = w.weight_class_id 
                AND w.active = TRUE 
                AND w.year_id = (SELECT id FROM years WHERE is_current = TRUE)
            WHERE wc.active = TRUE
            GROUP BY wc.id, wc.name, wc.division, wc.max_weight
            ORDER BY wc.division, wc.max_weight
        """)
        weight_distribution = cursor.fetchall()
        
        return render_template('admin/roster.html', title='Roster Management', 
                             stats=stats, weight_distribution=weight_distribution)
        
    except psycopg2.Error as e:
        flash('Error loading roster data.', 'error')
        print(f"Roster dashboard error: {e}")
        return redirect(url_for('admin_dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/wrestlers')
@login_required
@role_required(['admin', 'coach'])
def admin_wrestlers():
    """Wrestler management page"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_roster'))
    
    try:
        cursor = conn.cursor()
        
        # Get all wrestlers with details
        cursor.execute("""
            SELECT w.id, w.first_name, w.last_name, w.division, w.level, w.rank_in_division,
                   w.grade, w.wins, w.losses, w.active, w.created_at,
                   wc.name as weight_class_name,
                   wd.role as wrestler_role,
                   y.school_year
            FROM wrestlers w
            LEFT JOIN weightClasses wc ON w.weight_class_id = wc.id
            LEFT JOIN wrestlerDetails wd ON w.id = wd.wrestler_id
            LEFT JOIN years y ON w.year_id = y.id
            ORDER BY y.start_year DESC, w.division, w.level, wc.max_weight, w.rank_in_division
        """)
        wrestlers = cursor.fetchall()
        
        return render_template('admin/wrestlers.html', title='Wrestler Management', wrestlers=wrestlers)
        
    except psycopg2.Error as e:
        flash('Error loading wrestlers.', 'error')
        print(f"Wrestlers management error: {e}")
        return redirect(url_for('admin_roster'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/staff')
@login_required
@role_required(['admin', 'coach'])
def admin_staff():
    """Staff management page"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_roster'))
    
    try:
        cursor = conn.cursor()
        
        # Get all staff with details
        cursor.execute("""
            SELECT s.id, s.first_name, s.last_name, s.role, s.email, s.phone_number,
                   s.active, s.created_at,
                   sd.years_coaching,
                   y.school_year
            FROM staff s
            LEFT JOIN staffDetails sd ON s.id = sd.staff_id
            LEFT JOIN years y ON s.year_id = y.id
            ORDER BY y.start_year DESC, 
                CASE s.role 
                    WHEN 'head_coach' THEN 1
                    WHEN 'assistant_coach' THEN 2
                    WHEN 'manager' THEN 3
                    ELSE 4
                END,
                s.last_name, s.first_name
        """)
        staff = cursor.fetchall()
        
        return render_template('admin/staff.html', title='Staff Management', staff=staff)
        
    except psycopg2.Error as e:
        flash('Error loading staff.', 'error')
        print(f"Staff management error: {e}")
        return redirect(url_for('admin_roster'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/create-wrestler', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'coach'])
def admin_create_wrestler():
    """Create new wrestler"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_wrestlers'))
    
    try:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            weight_class_id = request.form.get('weight_class_id')
            division = request.form.get('division')
            level = request.form.get('level')
            rank_in_division = request.form.get('rank_in_division', 1)
            grade = request.form.get('grade')
            email = request.form.get('email')
            
            # Validation
            if not all([first_name, last_name, weight_class_id, division, level, grade]):
                flash('Required fields: First Name, Last Name, Weight Class, Division, Level, Grade', 'error')
                return redirect(url_for('admin_create_wrestler'))
            
            # Get current year
            cursor.execute("SELECT id FROM years WHERE is_current = TRUE LIMIT 1")
            current_year = cursor.fetchone()
            if not current_year:
                flash('No current school year set.', 'error')
                return redirect(url_for('admin_wrestlers'))
            
            # Insert wrestler
            cursor.execute("""
                INSERT INTO wrestlers (first_name, last_name, weight_class_id, division, level, 
                                     rank_in_division, grade, email, year_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (first_name, last_name, weight_class_id, division, level, 
                  rank_in_division, grade, email or None, current_year['id']))
            
            wrestler_id = cursor.fetchone()['id']
            
            # Create wrestler details record
            cursor.execute("""
                INSERT INTO wrestlerDetails (wrestler_id) VALUES (%s)
            """, (wrestler_id,))
            
            conn.commit()
            flash(f'Wrestler {first_name} {last_name} created successfully!', 'success')
            return redirect(url_for('admin_wrestlers'))
        
        # GET request - show form
        # Get available divisions
        cursor.execute("SELECT DISTINCT division FROM weightClasses WHERE active = TRUE ORDER BY division")
        divisions = cursor.fetchall()
        
        # Get weight classes grouped by division
        cursor.execute("""
            SELECT id, name, max_weight, division, level 
            FROM weightClasses 
            WHERE active = TRUE 
            ORDER BY division, max_weight
        """)
        weight_classes = cursor.fetchall()
        
        return render_template('admin/create_wrestler.html', 
                             title='Create Wrestler', 
                             weight_classes=weight_classes,
                             divisions=divisions)
        
    except psycopg2.Error as e:
        flash('Error creating wrestler.', 'error')
        print(f"Create wrestler error: {e}")
        return redirect(url_for('admin_wrestlers'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/create-staff', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'coach'])
def admin_create_staff():
    """Create new staff member"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_staff'))
    
    try:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            role = request.form.get('role')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            
            # Validation
            if not all([first_name, last_name, role]):
                flash('Required fields: First Name, Last Name, Role', 'error')
                return redirect(url_for('admin_create_staff'))
            
            # Get current year
            cursor.execute("SELECT id FROM years WHERE is_current = TRUE LIMIT 1")
            current_year = cursor.fetchone()
            if not current_year:
                flash('No current school year set.', 'error')
                return redirect(url_for('admin_staff'))
            
            # Insert staff
            cursor.execute("""
                INSERT INTO staff (first_name, last_name, role, email, phone_number, year_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (first_name, last_name, role, email or None, phone_number or None, current_year['id']))
            
            staff_id = cursor.fetchone()['id']
            
            # Create staff details record
            cursor.execute("""
                INSERT INTO staffDetails (staff_id) VALUES (%s)
            """, (staff_id,))
            
            conn.commit()
            flash(f'Staff member {first_name} {last_name} created successfully!', 'success')
            return redirect(url_for('admin_staff'))
        
        # GET request - show form
        return render_template('admin/create_staff.html', title='Create Staff Member')
        
    except psycopg2.Error as e:
        flash('Error creating staff member.', 'error')
        print(f"Create staff error: {e}")
        return redirect(url_for('admin_staff'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/edit-staff/<int:staff_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'coach'])
def admin_edit_staff(staff_id):
    """Edit staff member"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_staff'))
    
    try:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            role = request.form.get('role')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            
            # Validation
            if not all([first_name, last_name, role]):
                flash('Required fields: First Name, Last Name, Role', 'error')
                return redirect(url_for('admin_edit_staff', staff_id=staff_id))
            
            # Update staff
            cursor.execute("""
                UPDATE staff 
                SET first_name = %s, last_name = %s, role = %s, email = %s, phone_number = %s, modified_at = %s
                WHERE id = %s
            """, (first_name, last_name, role, email or None, phone_number or None, datetime.utcnow(), staff_id))
            conn.commit()
            
            flash('Staff member updated successfully!', 'success')
            return redirect(url_for('admin_staff'))
        
        # GET request - show form
        cursor.execute("""
            SELECT id, first_name, last_name, role, email, phone_number
            FROM staff WHERE id = %s
        """, (staff_id,))
        staff_member = cursor.fetchone()
        
        if not staff_member:
            flash('Staff member not found.', 'error')
            return redirect(url_for('admin_staff'))
        
        return render_template('admin/edit_staff.html', staff_member=staff_member, title='Edit Staff Member')
        
    except psycopg2.Error as e:
        flash('Database error.', 'error')
        print(f"Edit staff error: {e}")
        return redirect(url_for('admin_staff'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/weight-classes')
@login_required
@role_required(['admin', 'coach'])
def admin_weight_classes():
    """Manage weight classes and divisions"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor = conn.cursor()
        
        # Get weight classes grouped by division
        cursor.execute("""
            SELECT division, 
                   COUNT(*) as weight_class_count,
                   MIN(max_weight) as min_weight,
                   MAX(max_weight) as max_weight_limit
            FROM weightClasses 
            WHERE active = TRUE 
            GROUP BY division 
            ORDER BY division
        """)
        division_stats = cursor.fetchall()
        
        # Get all weight classes for detailed view
        cursor.execute("""
            SELECT id, name, max_weight, division, level, active
            FROM weightClasses 
            ORDER BY division, max_weight
        """)
        all_weight_classes = cursor.fetchall()
        
        return render_template('admin/weight_classes.html', 
                             title='Weight Class Management',
                             division_stats=division_stats,
                             all_weight_classes=all_weight_classes)
        
    except psycopg2.Error as e:
        flash('Database error.', 'error')
        print(f"Weight classes error: {e}")
        return redirect(url_for('admin_dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/create-weight-class', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'coach'])
def admin_create_weight_class():
    """Create new weight class"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_weight_classes'))
    
    try:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Get form data
            max_weight = request.form.get('max_weight')
            division = request.form.get('division')
            custom_division = request.form.get('custom_division')
            level = request.form.get('level')
            name = request.form.get('name')
            
            # Use custom division if provided, otherwise use selected division
            final_division = custom_division.strip() if custom_division else division
            
            # Validation
            if not all([max_weight, final_division, level]):
                flash('Required fields: Weight Limit, Division, Level', 'error')
                return redirect(url_for('admin_create_weight_class'))
            
            try:
                max_weight = int(max_weight)
            except ValueError:
                flash('Weight limit must be a number.', 'error')
                return redirect(url_for('admin_create_weight_class'))
            
            # Create name if not provided
            if not name:
                name = f"{max_weight} lbs {final_division}"
            
            # Insert weight class
            cursor.execute("""
                INSERT INTO weightClasses (name, max_weight, division, level)
                VALUES (%s, %s, %s, %s)
            """, (name, max_weight, final_division, level))
            
            conn.commit()
            flash(f'Weight class {max_weight} lbs ({final_division}) created successfully!', 'success')
            return redirect(url_for('admin_weight_classes'))
        
        # GET request - show form
        # Get existing divisions
        cursor.execute("SELECT DISTINCT division FROM weightClasses ORDER BY division")
        existing_divisions = cursor.fetchall()
        
        return render_template('admin/create_weight_class.html', 
                             title='Create Weight Class',
                             existing_divisions=existing_divisions)
        
    except psycopg2.Error as e:
        flash('Error creating weight class.', 'error')
        print(f"Create weight class error: {e}")
        return redirect(url_for('admin_weight_classes'))
    finally:
        cursor.close()
        conn.close()

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