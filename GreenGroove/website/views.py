from datetime import datetime, time, timedelta
import os
import uuid
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from website.models import Comment, User, Event, db, Order

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get all events for the "Popular Events" section
    events = Event.query.all()

    # Get the current date and time
    today = datetime.now()

    # Calculate the date for 7 days from now
    next_week = today + timedelta(days=7)

    # Filter events that are happening this week
    events_this_week = Event.query.filter(Event.date >= today, Event.date <= next_week).all()

    print(events)  # To check popular events
    print(events_this_week)  # To check events this week
    
    # Pass both event sets to the template
    return render_template('index.html', events=events, events_this_week=events_this_week)


@main_bp.route('/createEvent', methods=['GET', 'POST'])
@login_required
def createEvent():
    if request.method == 'POST':
        # Get form data from the request
        event_name = request.form.get('eventName')
        
        # Check if an event with the same name already exists
        existing_event = Event.query.filter_by(event_name=event_name).first()
        if existing_event:
            flash(f"An event with the name '{event_name}' already exists. Please choose a different name.", 'danger')
            return redirect(url_for('main.createEvent'))

        artist_name = request.form.get('artistName')
        venue = request.form.get('venue')
        description = request.form.get('description')
        date_str = request.form.get('date')  # Get date as string from form
        start_time_str = request.form.get('startTime')
        end_time_str = request.form.get('endTime')
        price = request.form.get('price')
        ticket_amount = request.form.get('tickets')

        # Convert date and time to Python objects (using DD/MM/YYYY format for the date)
        event_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        # Handle image upload
        image = request.files['image']
        if image and image.filename != '':
            filename = secure_filename(image.filename)

            # Get the absolute path for the uploads folder
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            image_url = f'uploads/{filename}'

        else:
            image_url = None  # No image uploaded

        # Create new event and save it to the database, including owner_id
        new_event = Event(
            event_name=event_name,
            artist_name=artist_name,
            venue=venue,
            description=description,
            date=event_date,
            start_time=start_time,
            end_time=end_time,
            price=price,
            ticket_amount=ticket_amount,
            image_path=image_url,
            owner_id=current_user.id  # Set the owner_id to the current logged-in user's ID
        )
        
        # Add and commit the event to the database
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('main.eventDetails', event_id=new_event.id))

    return render_template('createEvent.html')

@main_bp.route('/BookingHistory')
@login_required
def BookingHistory():
    return render_template('BookingHistory.html')


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

@main_bp.route('/event/<int:event_id>', methods=['GET', 'POST'])
def eventDetails(event_id):
    # Fetch the main event from the database
    event = Event.query.get_or_404(event_id)

    # Handle POST request (form submission for comments)
    if request.method == 'POST':
        comment_content = request.form.get('comment')
        if comment_content:
            new_comment = Comment(
                content=comment_content,
                user_id=current_user.id,  # The ID of the logged-in user
                event_id=event_id         # The ID of the current event
            )
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added successfully!', 'success')
            return redirect(url_for('main.eventDetails', event_id=event_id))

    # Fetch other events (excluding the current event)
    other_events = Event.query.filter(Event.id != event_id).limit(4).all()

    # Pass the main event and other events to the template for rendering the full page
    return render_template('eventDetails.html', event=event, other_events=other_events)

@main_bp.route('/event/<int:event_id>/details', methods=['GET'])
def get_event_details(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Log event details for debugging
    print(f"Event fetched: {event.event_name}, {event.date}, {event.price}")
    
    return jsonify({
        'event_name': event.event_name,
        'price': event.price,
        'date': event.date.strftime('%d.%m.%Y'),
        'start_time': event.start_time.strftime('%I:%M %p'),
        'end_time': event.end_time.strftime('%I:%M %p'),
        'venue': event.venue,
        'description': event.description,
        'image_path': url_for('static', filename=event.image_path),
        'status': event.status
    })




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
            image_path="uploads/jazz_event.jpg",
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
            image_path="uploads/rock_event.jpg",
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
            image_path="uploads/classical_event.jpg",
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
            image_path="uploads/festival_event.jpg",
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
            image_path="uploads/theatre_event.jpg",
            description="A captivating theatre performance.",
            owner_id=1
        )
    ]

    # Add events to the session and commit them to the database
    for event in events:
        db.session.add(event)
    db.session.commit()

    return "5 events added successfully."

@main_bp.route('/findEvents')
def findEvents():
    # Query the database to get all events
    events = Event.query.all()
    
    # Pass the events to the template
    return render_template('findEvents.html', events=events)

@main_bp.route('/show-events')
def show_events():
    events = Event.query.all()
    event_list = [f"ID: {event.id}, Name: {event.event_name}" for event in events]
    return "<br>".join(event_list)
