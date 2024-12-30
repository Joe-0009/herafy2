#auth.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from .. import db
from ..forms import RegistrationForm, LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully!', category='success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home.index'))
        else:
            flash('Invalid email or password.', category='error')
    return render_template("auth/login.html", form=form)

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password1.data, method='pbkdf2:sha256')
        new_user = User(
            email=form.email.data, 
            username=form.username.data, 
            password=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(new_user)
        try:
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('profile.view_profile', user_id=new_user.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', category='error')
            print(f"Error during user registration: {str(e)}")
    return render_template("auth/sign_up.html", form=form)