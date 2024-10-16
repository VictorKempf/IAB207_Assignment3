from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/createEvent')
def createEvent():
    return render_template('createEvent.html')

@main_bp.route('/BookingHistory')
def BookingHistory():
    return render_template('BookingHistory.html')

@main_bp.route('/eventDetails')
def eventDetails():
    return render_template('eventDetails.html')