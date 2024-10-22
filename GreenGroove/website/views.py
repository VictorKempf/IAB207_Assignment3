from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/createEvent')
@login_required
def createEvent():
    return render_template('createEvent.html')

@main_bp.route('/BookingHistory')
@login_required
def BookingHistory():
    return render_template('BookingHistory.html')

@main_bp.route('/eventDetails')
def eventDetails():
    return render_template('eventDetails.html')

@main_bp.route('/purchaseTickets')
@login_required
def purchaseTickets():
    return render_template('purchaseTickets.html')