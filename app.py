from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# For now, we'll use a simple database URL that won't cause connection issues during development
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///local_wrestling.db')

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

if __name__ == '__main__':
    # Development server settings
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    print("🤼 Starting Southern Lee Wrestling website...")
    print("📱 Local development server: http://127.0.0.1:5000")
    print("⚔️ Find A Way! - Cavaliers Wrestling")
    app.run(debug=debug_mode, host='127.0.0.1', port=5000) 