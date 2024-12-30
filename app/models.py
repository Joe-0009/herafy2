from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date, datetime
import enum

class ApplicationStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    
accepted_applicants = db.Table('accepted_applicants',
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    about_me = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    skills = db.relationship('Skill', backref='user', lazy=True, cascade="all, delete-orphan")
    experiences = db.relationship('Experience', backref='user', lazy=True, cascade="all, delete-orphan")
    certifications = db.relationship('Certification', backref='user', lazy=True, cascade="all, delete-orphan")
    posted_jobs = db.relationship('Job', backref='poster', lazy=True, foreign_keys='Job.poster_id')
    
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', back_populates='reviewer')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', back_populates='reviewee')

    applications = db.relationship('Application', back_populates='applicant', lazy=True)
    accepted_jobs = db.relationship('Job', secondary=accepted_applicants, backref=db.backref('accepted_workers', lazy='dynamic'))

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __repr__(self):
        return f'<User {self.username}>'

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Skill {self.name}>'

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Experience {self.title} at {self.company}>'

class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Certification {self.name}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    jobs = db.relationship('Job', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    profession = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.OPEN, nullable=False)
    date_posted = db.Column(db.DateTime, default=func.now(), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    budget = db.Column(db.Float, nullable=True)
    expected_duration = db.Column(db.String(50), nullable=True)
    required_skills = db.Column(db.String(200), nullable=True)
    
    applications = db.relationship('Application', back_populates='job', lazy=True)
    reviews = db.relationship('Review', back_populates='job', lazy=True)
    pictures = db.relationship('JobPicture', backref='job', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Job {self.title}>'

class JobPicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_applied = db.Column(db.DateTime, default=func.now(), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.IN_PROGRESS, nullable=False)

    job = db.relationship('Job', back_populates='applications', lazy=True)
    applicant = db.relationship('User', back_populates='applications', lazy=True)

    def __repr__(self):
        return f'<Application {self.id} for Job {self.job_id}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=func.now(), nullable=False)
    
    job = db.relationship('Job', back_populates='reviews')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], back_populates='reviews_given')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], back_populates='reviews_received')
    
    def __repr__(self):
        return f'<Review {self.id} by User {self.reviewer_id} for User {self.reviewee_id}>'
    
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'<Message {self.id} from User {self.sender_id} to User {self.receiver_id}>'
