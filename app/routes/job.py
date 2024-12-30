import os
from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..forms import JobForm, DummyForm, RatingForm, AcceptApplicationForm, PROFESSIONS, MOROCCAN_CITIES, SearchJobsForm
from ..models import Job, User, Application, Review, JobPicture, ApplicationStatus, accepted_applicants
from .. import db
from datetime import datetime, timezone
from PIL import Image
from sqlalchemy.exc import IntegrityError

job = Blueprint('job', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_pictures(pictures):
    """Save and resize uploaded job pictures, return filenames."""
    picture_filenames = []
    for picture in pictures:
        if picture.filename:
            filename = secure_filename(picture.filename)
            _, ext = os.path.splitext(filename)
            new_filename = f"{current_user.id}_{datetime.now().timestamp()}{ext}"
            picture_path = os.path.join(current_app.config['UPLOAD_FOLDER2'], new_filename)
            
            # Resize image
            output_size = (800, 600)
            img = Image.open(picture)
            img.thumbnail(output_size)
            img.save(picture_path)
            
            picture_filenames.append(new_filename)
    return picture_filenames

@job.route('/post', methods=['GET', 'POST'])
@login_required
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            profession=form.profession.data,
            location=form.location.data,
            budget=form.budget.data,
            expected_duration=form.expected_duration.data,
            required_skills=form.required_skills.data,
            poster_id=current_user.id
        )
        db.session.add(new_job)
        db.session.flush()  # This assigns an ID to new_job

        # Handle picture uploads
        if form.pictures.data:
            for picture in form.pictures.data:
                if picture and allowed_file(picture.filename):
                    filename = secure_filename(picture.filename)
                    picture.save(os.path.join(current_app.config['UPLOAD_FOLDER2'], filename))
                    job_picture = JobPicture(filename=filename, job_id=new_job.id)
                    db.session.add(job_picture)

        db.session.commit()
        flash('Your job has been posted!', 'success')
        return redirect(url_for('job.view_jobs' ))
    return render_template('job/post_job.html', title='Post a Job', form=form)



@job.route('/jobs', methods=['GET', 'POST'])
def view_jobs():
    form = SearchJobsForm()
    
    # Initialize variables
    location = None
    profession = None
    results = None
    
    # Handle both POST (form submission) and GET (URL parameters) requests
    if form.validate_on_submit() or request.method == 'GET':
        # Get filter parameters from form or URL
        location = form.location.data or request.args.get('location')
        profession = form.profession.data or request.args.get('profession')
        
        # Query jobs based on filters
        jobs_query = Job.query.filter(Job.status == ApplicationStatus.OPEN)
        
        if location and location != 'All':
            jobs_query = jobs_query.filter(Job.location == location)
        if profession and profession != 'All':
            jobs_query = jobs_query.filter(Job.profession == profession)
        
        # Sort jobs by date_posted in descending order
        jobs_query = jobs_query.order_by(Job.date_posted.desc())
        
        results = jobs_query.all()
    
    # If no filters applied, get all open jobs sorted by date
    if not results and location == 'All' and profession == 'All':
        jobs = Job.query.filter(Job.status == ApplicationStatus.OPEN).order_by(Job.date_posted.desc()).all()
    else:
        jobs = results
    
    # Pre-fill form with current filter values
    form.location.data = location
    form.profession.data = profession
    
    return render_template('job/view_jobs.html',
                           jobs=jobs,
                           results=results,
                           ApplicationStatus=ApplicationStatus,
                           form=form,
                           cities=MOROCCAN_CITIES,
                           professions=PROFESSIONS)



@job.route('/delete-job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.poster_id != current_user.id:
        flash('You do not have permission to delete this job', 'danger')
        return redirect(url_for('job.view_jobs'))
    
    try:
        # Delete associated reviews
        Review.query.filter_by(job_id=job_id).delete()
        
        # Delete associated applications
        Application.query.filter_by(job_id=job_id).delete()
        
        # Delete the job
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job: {str(e)}")
        flash('An error occurred while deleting the job.', 'danger')
    
    return redirect(url_for('job.view_jobs'))

@job.route('/apply-job/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status != ApplicationStatus.OPEN:
        flash('This job is no longer open for applications', 'warning')
        return redirect(url_for('job.view_jobs'))
    
    application = Application.query.filter_by(job_id=job_id, worker_id=current_user.id).first()
    if application:
        flash('You have already applied for this job', 'warning')
    else:
        new_application = Application(job_id=job_id, worker_id=current_user.id, date_applied=datetime.now(timezone.utc))
        db.session.add(new_application)
        db.session.commit()
        flash('Successfully applied for the job!', 'success')
    return redirect(url_for('job.view_jobs'))

@job.route('/finish-job/<int:job_id>', methods=['POST'])
@login_required
def finish_job(job_id):
    job = Job.query.get_or_404(job_id)

    if job.poster_id != current_user.id:
        flash('You do not have permission to finish this job', 'error')
        return redirect(url_for('job.job_details', job_id=job_id))

    if job.status != ApplicationStatus.IN_PROGRESS:
        flash('This job cannot be finished at this time', 'warning')
        return redirect(url_for('job.job_details', job_id=job_id))

    job.status = ApplicationStatus.COMPLETED
    db.session.commit()
    flash('Job marked as finished. Please rate the workers.', 'success')
    return redirect(url_for('job.rate_job', job_id=job_id))


@job.route('/rate-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def rate_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.status != ApplicationStatus.COMPLETED:
        flash('You can only rate a finished job', 'danger')
        return redirect(url_for('job.view_jobs'))
    
    # Get the accepted application for this job
    accepted_application = Application.query.filter_by(job_id=job_id, status=ApplicationStatus.ACCEPTED).first()
    
    if not accepted_application:
        flash('No accepted worker found for this job', 'danger')
        return redirect(url_for('job.view_jobs'))
    
    form = RatingForm()
    if form.validate_on_submit():
        new_review = Review(
            job_id=job.id,
            reviewer_id=current_user.id,
            reviewee_id=accepted_application.worker_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Rating submitted successfully!', 'success')
        return redirect(url_for('job.view_jobs'))
    
    return render_template('job/rate_job.html', form=form, job=job, worker=accepted_application.applicant)


@job.route('/job_details/<int:job_id>', methods=['GET'])
@login_required
def job_details(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        applications = Application.query.filter_by(job_id=job_id).order_by(Application.date_applied.desc()).all()
        form = AcceptApplicationForm()
        
        return render_template('job/job_details.html',
                               job=job,
                               applications=applications,
                               form=form,
                               ApplicationStatus=ApplicationStatus)
    except Exception as e:
        current_app.logger.error(f"Error in job_details: {str(e)}")
        return "An error occurred while loading job details.", 500
    
    


@job.route('/accept-application/<int:job_id>/<int:application_id>', methods=['POST'])
@login_required
def accept_application(job_id, application_id):
    job = Job.query.get_or_404(job_id)
    application = Application.query.get_or_404(application_id)

    if job.poster_id != current_user.id:
        flash('You are not authorized to accept applications for this job.', 'error')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    if application.job_id != job_id:
        flash('This application does not belong to this job.', 'error')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    if application.status == ApplicationStatus.ACCEPTED:
        flash('This application has already been accepted.', 'info')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    application.status = ApplicationStatus.ACCEPTED
    job.status = ApplicationStatus.IN_PROGRESS

    # Reject all other applications for this job
    for other_application in job.applications:
        if other_application.id != application.id:
            other_application.status = ApplicationStatus.REJECTED

    db.session.commit()

    flash('Application accepted successfully!', 'success')
    return redirect(url_for('profile.view_profile', user_id=current_user.id))




@job.route('/reject-application/<int:job_id>/<int:application_id>', methods=['POST'])
@login_required
def reject_application(job_id, application_id):
    job = Job.query.get_or_404(job_id)
    application = Application.query.get_or_404(application_id)

    if job.poster_id != current_user.id:
        flash('You do not have permission to reject this application.', 'danger')
        return redirect(url_for('job.job_details', job_id=job_id))

    if application.job_id != job_id:
        flash('Invalid application for this job.', 'danger')
        return redirect(url_for('job.job_details', job_id=job_id))

    application.status = ApplicationStatus.REJECTED
    db.session.commit()

    flash('Application has been rejected.', 'success')
    return redirect(url_for('job.job_details', job_id=job_id))