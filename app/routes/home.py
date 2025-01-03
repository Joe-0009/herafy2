#home.py
import json
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .. import db

home = Blueprint('home', __name__)

@home.route('', methods=['GET', 'POST'])
def index():
    
        
    return render_template("home/index.html")


