from datetime import datetime, time
import uuid
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from website.models import User, Event, db, Order

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

@main_bp.route('/purchaseTickets/<int:event_id>', methods=['GET', 'POST'])
@login_required
def purchase_tickets(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('name')
        last_name = request.form.get('lastname')
        quantity = int(request.form.get('quantity'))

        # Check if quantity is valid
        if quantity <= 0:
            flash('Quantity must be greater than 0', 'danger')
            return redirect(url_for('purchase_tickets', event_id=event_id))

        # Calculate total price
        total_price = event.price * quantity

        # Create a unique order ID
        order_id = str(uuid.uuid4())

        # Create new order entry
        new_order = Order(
            order_id=order_id,
            user_id=current_user.id,
            event_id=event.id,
            quantity=quantity,
            total_price=total_price,
            booking_date=datetime.now()
        )

        # Save the order in the database
        db.session.add(new_order)
        db.session.commit()

        # Redirect to confirmation page with the new order ID
        return redirect(url_for('confirmation', order_id=new_order.id))

    return render_template('purchaseTickets.html', event=event)

main_bp.route('/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    # Get the order by ID
    order = Order.query.get_or_404(order_id)
    
    # Ensure the current user is the owner of the order
    if order.user_id != current_user.id:
        abort(403)  # Forbidden access

    # Get the event associated with the order
    event = Event.query.get_or_404(order.event_id)

    # Render the confirmation page with user, event, and order data
    return render_template('confirmation.html', 
                           user=current_user, 
                           event=event, 
                           order=order)

@main_bp.route('/event/<int:event_id>')
def event_details(event_id):
    # Fetch the main event from the database
    event = Event.query.get_or_404(event_id)

    # Fetch other events (excluding the current event)
    other_events = Event.query.filter(Event.id != event_id).limit(4).all()

    # Pass the main event and other events to the template
    return render_template('eventDetails.html', event=event, other_events=other_events)

@main_bp.route('/check_data')
def check_data():
    # Check if there are any events
    if not Event.query.first():
        return "No events found in the database."
    else:
        return "Events are present in the database."
@main_bp.route('/add_test_events')
def add_test_events():
    # Create multiple events
    events = [
        Event(
            event_name="Brisbane Jazz Night",
            artist_name="Smooth Jazz Band",
            venue="Brisbane City Hall",
            date=datetime(2024, 11, 5),
            start_time=time(18, 0),
            end_time=time(22, 0),
            ticket_amount=150,
            price=30.00,
            image_path="path/to/jazz_event.jpg",
            description="A night of smooth jazz with local artists.",
            owner_id=1
        ),
        Event(
            event_name="Brisbane Rock Revival",
            artist_name="Revival Band",
            venue="Brisbane Stadium",
            date=datetime(2024, 10, 30),
            start_time=time(19, 0),
            end_time=time(23, 0),
            ticket_amount=200,
            price=50.00,
            image_path="path/to/rock_event.jpg",
            description="Rock out with Brisbane's best bands.",
            owner_id=1
        ),
        Event(
            event_name="Classical Music Concert",
            artist_name="Brisbane Symphony Orchestra",
            venue="Brisbane Opera House",
            date=datetime(2024, 12, 1),
            start_time=time(20, 0),
            end_time=time(22, 30),
            ticket_amount=100,
            price=40.00,
            image_path="path/to/classical_event.jpg",
            description="An evening of classical music featuring renowned orchestras.",
            owner_id=1
        ),
        Event(
            event_name="Brisbane Music Festival",
            artist_name="Various Artists",
            venue="Brisbane Parklands",
            date=datetime(2024, 9, 21),
            start_time=time(12, 0),
            end_time=time(22, 0),
            ticket_amount=500,
            price=75.00,
            image_path="path/to/festival_event.jpg",
            description="A full day of music performances featuring local and international artists.",
            owner_id=1
        ),
        Event(
            event_name="Theatre Night",
            artist_name="Brisbane Theatre Group",
            venue="Brisbane Theatre",
            date=datetime(2024, 11, 15),
            start_time=time(19, 0),
            end_time=time(22, 30),
            ticket_amount=120,
            price=45.00,
            image_path="path/to/theatre_event.jpg",
            description="A captivating theatre performance.",
            owner_id=1
        )
    ]

    # Add events to the session and commit them to the database
    for event in events:
        db.session.add(event)
    db.session.commit()

    return "5 events added successfully."
