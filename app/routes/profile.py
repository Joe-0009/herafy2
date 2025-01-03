import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import UpdateProfileForm, AddSkillForm, AddExperienceForm, DummyForm
from ..models import User, Skill, Experience, Job, Review, Application, ApplicationStatus
from .. import db
from sqlalchemy.sql import func
from PIL import Image


# Define the Blueprint for the profile module
profile = Blueprint('profile', __name__)

def save_picture(file):
    """Save and resize uploaded profile picture, return filename."""
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Ensure the file is an image
    if not file.content_type.startswith('image/'):
        flash('Invalid file type. Please upload an image.', 'error')
        return None

    # Ensure the file size is within acceptable limits
    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
        flash('File too large. Please upload a smaller image.', 'error')
        return None

    # Define the new filename with user ID and the original extension
    _, ext = os.path.splitext(filename)
    new_filename = f"{current_user.id}{ext}"
    
    # Define the upload folder and create it if it doesn't exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # Define the full file path
    filepath = os.path.join(upload_folder, new_filename)
    
    try:
        # Resize the image to 250x250 pixels
        output_size = (250, 250)
        img = Image.open(file)
        img.thumbnail(output_size)
        img.save(filepath)
    except Exception as e:
        flash('An error occurred while processing the image.', 'error')
        return None
    
    return new_filename

@profile.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    """View user profile."""
    # Query the user by ID, or return a 404 error if not found
    profile_user = User.query.get_or_404(user_id)
    
    # Calculate the average rating from reviews
    average_rating = db.session.query(func.avg(Review.rating)).filter_by(reviewee_id=user_id).scalar() or 0
    
    # Get the list of applied jobs, posted jobs, and reviews
    if current_user.id == profile_user.id:    
        posted_jobs = Job.query.filter_by(poster_id=current_user.id).order_by(Job.date_posted.desc()).all()
        applied_jobs = Application.query.filter_by(worker_id=current_user.id).order_by(Application.date_applied.desc()).all()
    else:
        applied_jobs = []
        posted_jobs = []
    
    reviews = Review.query.filter_by(reviewee_id=user_id).all()
    
    # Render the profile template with the necessary data
    return render_template('profile/profile.html', 
                           profile_user=profile_user, 
                           average_rating=average_rating,
                           add_skill_form=AddSkillForm(),
                           add_experience_form=AddExperienceForm(),
                           form=DummyForm(), 
                           applied_jobs=applied_jobs,
                           posted_jobs=posted_jobs,
                           reviews=reviews,
                           ApplicationStatus=ApplicationStatus)

@profile.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Update user profile."""
    form = UpdateProfileForm()
    if form.validate_on_submit():
        # Update the current user's profile information with form data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.location = form.location.data
        current_user.profession = form.profession.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.about_me = form.about_me.data
        
        # Update the profile picture if provided
        if form.profile_picture.data:
            if current_user.profile_picture:
                # Delete the old profile picture
                old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.profile_picture)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            current_user.profile_picture = save_picture(form.profile_picture.data)
        
        # Commit the changes to the database
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))
    
    # Pre-populate the form with the current user's data
    form.process(obj=current_user)
    return render_template('profile/update_profile.html', form=form)

@profile.route('/add-skill', methods=['POST'])
@login_required
def add_skill():
    """Add a new skill to user profile."""
    form = AddSkillForm()
    if form.validate_on_submit():
        # Check for duplicate skills
        if Skill.query.filter_by(name=form.skill.data, user_id=current_user.id).first():
            return jsonify(success=False, message='Skill already exists.')
        else:
            # Add the new skill to the database
            skill = Skill(name=form.skill.data, user_id=current_user.id)
            db.session.add(skill)
            db.session.commit()
            return jsonify(success=True, message='Skill added successfully!')
    else:
        return jsonify(success=False, message='Failed to add skill. Please try again.')

@profile.route('/add-experience', methods=['POST'])
@login_required
def add_experience():
    """Add a new experience to user profile."""
    form = AddExperienceForm()
    if form.validate_on_submit():
        # Check for duplicate experiences
        if Experience.query.filter_by(title=form.experience.data, company=form.company.data, user_id=current_user.id).first():
            return jsonify(success=False, message='Experience already exists.')
        else:
            # Add the new experience to the database
            experience = Experience(
                title=form.experience.data,
                company=form.company.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                description=form.description.data,
                user_id=current_user.id
            )
            db.session.add(experience)
            db.session.commit()
            return jsonify(success=True, message='Experience added successfully!')
    else:
        return jsonify(success=False, message='Failed to add experience. Please try again.')

