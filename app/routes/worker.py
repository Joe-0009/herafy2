from flask import render_template, request, Blueprint
from flask_login import login_required
from ..models import User
from ..forms import SearchWorkersForm

worker = Blueprint('worker', __name__)

@worker.route('/search', methods=['GET', 'POST'])
@login_required
def search_workers():
    form = SearchWorkersForm()
    results = []

    if form.validate_on_submit():
        location = form.location.data
        profession = form.profession.data
        results = User.query.filter_by(location=location, profession=profession).all()

    return render_template('worker/search_workers.html', form=form, results=results)