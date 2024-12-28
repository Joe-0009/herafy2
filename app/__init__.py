from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import timeago
from datetime import datetime

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration settings
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/profile_pics')
    app.config['UPLOAD_FOLDER2'] = os.path.join(app.root_path, 'static/uploads')
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    # Register Jinja2 filter
    app.jinja_env.filters['timeago'] = lambda date: timeago.format(date, datetime.utcnow())
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.routes.auth import auth
    from app.routes.home import home
    from app.routes.profile import profile
    from app.routes.job import job
    from app.routes.worker import worker
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(job, url_prefix='/job')
    app.register_blueprint(worker, url_prefix='/worker')
    
    # Import models
    from .models import User, Skill, Experience, Certification, Job, Review
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Configure login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    database_path = os.path.join(app.root_path, 'database.db')
    if not os.path.exists(database_path):
        with app.app_context():
            db.create_all()
            print('Created Database!')