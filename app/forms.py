#forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField, DateField, MultipleFileField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from .models import User
from flask_wtf.file import FileAllowed
from datetime import datetime

# List of Moroccan cities
MOROCCAN_CITIES = [('All', 'All Cities')] + [
    ('Casablanca', 'Casablanca'),
    ('Rabat', 'Rabat'),
    ('Marrakech', 'Marrakech'),
    ('Kenitra', 'Kenitra'),
    ('Fes', 'Fes'),
    ('Tangier', 'Tangier'),
    ('Agadir', 'Agadir'),
    ('Oujda', 'Oujda'),
    ('Tetouan', 'Tetouan'),
    ('Safi', 'Safi')
]

# List of professions
PROFESSIONS = [('All', 'All Professions')] + [
    ('Electrician', 'Electrician'),
    ('Barber', 'Barber'),
    ('Tailor', 'Tailor'),
    ('Plumber', 'Plumber'),
    ('Cleaner', 'Cleaner'),
    ('Gardener', 'Gardener'),
    ('Painter', 'Painter'),
    ('Carpenter', 'Carpenter'),
    ('Mechanic', 'Mechanic'),
    ('Driver', 'Driver')
]

# Registration Form
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    first_name = StringField('First Name')  
    last_name = StringField('Last Name')    

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    submit = SubmitField('Sign Up')
# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Update Profile Form
class UpdateProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = SelectField('Location', choices=MOROCCAN_CITIES, validators=[DataRequired()])
    profession = SelectField('Profession', choices=PROFESSIONS, validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d')
    about_me = TextAreaField('About Me')
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')

# search jobs form
class SearchJobsForm(FlaskForm):
    location = SelectField('Location', choices=MOROCCAN_CITIES, validators=[DataRequired()])
    profession = SelectField('Profession', choices=PROFESSIONS, validators=[DataRequired()])
    submit = SubmitField('Search')
    
# Post Job Form
class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(message="Title is required."), Length(min=2, max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired(message="Description is required."), Length(min=10)])
    profession = SelectField('Profession', choices=PROFESSIONS, validators=[DataRequired(message="Profession is required.")])
    location = SelectField('Location', choices=MOROCCAN_CITIES, validators=[DataRequired(message="Location is required.")])
    budget = FloatField('Budget', validators=[DataRequired(message="Budget is required and must be a number.")])
    expected_duration = StringField('Expected Duration', validators=[DataRequired(message="Expected duration is required."), Length(max=50)])
    required_skills = StringField('Required Skills', validators=[DataRequired(message="Required skills are required."), Length(max=200)])
    pictures = MultipleFileField('Job Pictures', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Post Job')


# Search Workers Form
class SearchWorkersForm(FlaskForm):
    location = SelectField('Location', choices=MOROCCAN_CITIES, validators=[DataRequired()])
    profession = SelectField('Profession', choices=PROFESSIONS, validators=[DataRequired()])
    submit = SubmitField('Search')

# Add Skill Form
class AddSkillForm(FlaskForm):
    skill = StringField('Skill', validators=[DataRequired()])
    submit = SubmitField('Add Skill')

# Add Experience Form
class AddExperienceForm(FlaskForm):
    experience = StringField('Experience Title', validators=[DataRequired()])
    company = StringField('Company', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Experience')

# Dummy Form for generic actions like delete
class DummyForm(FlaskForm):
    submit = SubmitField('Delete')

# Rating Form for rating jobs
class RatingForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Rating')

# Application Form for applying to jobs
class ApplicationForm(FlaskForm):
    submit = SubmitField('Apply')

# Accept Application Form
class AcceptApplicationForm(FlaskForm):
    submit = SubmitField('Accept')
