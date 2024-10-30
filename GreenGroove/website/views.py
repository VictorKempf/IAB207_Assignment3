from datetime import datetime, time, timedelta
import os
import uuid
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from website.models import Comment, Artist, User, Event, db, Order
from sqlalchemy.orm import joinedload

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

    # Update status for all events before rendering
    for event in events + events_this_week:
        event.update_status()  # Ensure each event's status is up-to-date
    db.session.commit()  # Save any changes to the database

    print(events)  # To check popular events
    print(events_this_week)  # To check events this week
    
     # Get artists and their next upcoming event
    artists_next_event = []
    for artist in Artist.query.all():
        # Query the next event for each artist
        next_event = Event.query.filter(Event.artist_id == artist.id, Event.date >= today).order_by(Event.date).first()
        artists_next_event.append({
            'artist': artist,
            'next_event': next_event
        })

    # Pass both event sets and artists next event to the template
    return render_template('index.html', events=events, events_this_week=events_this_week, artists_next_event=artists_next_event)


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
        genre = request.form.get('genre')  # Get genre from the form

        # Convert date and time to Python objects (using DD/MM/YYYY format for the date)
        event_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        # Find the artist by name
        artist = Artist.query.filter_by(name=artist_name).first()
        if not artist:
            flash(f"Artist '{artist_name}' not found.", 'danger')
            return redirect(url_for('main.createEvent'))

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

        # Create new event and save it to the database, including genre and owner_id
        new_event = Event(
            event_name=event_name,
            artist_id=artist.id,
            venue=venue,
            description=description,
            date=event_date,
            start_time=start_time,
            end_time=end_time,
            price=price,
            ticket_amount=ticket_amount,
            image_path=image_url,
            genre=genre,  # Save genre here
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
    user_events = Event.query.filter_by(owner_id=current_user.id).all()
    return render_template('BookingHistory.html', events=user_events)

@main_bp.route('/artist/<int:artist_id>')
def artist_info(artist_id):
    # Query to get the artist and their associated events
    artist = Artist.query.options(joinedload(Artist.events)).get(artist_id)
    
    # If artist not found, return 404
    if not artist:
        abort(404)

    # Get all events by this artist
    events = artist.events  # Since we used joinedload, events should be preloaded

    # Render the artist information page
    return render_template('artistInfo.html', artist=artist, events=events)

@main_bp.route('/purchaseTickets/<int:event_id>', methods=['GET', 'POST'])
@login_required
def purchase_tickets(event_id):
    event = Event.query.get_or_404(event_id)

    # Prevent ticket purchase if the event is cancelled, inactive, or sold out
    if event.status in ['Cancelled', 'Inactive', 'Sold Out']:
        flash('Tickets cannot be purchased for this event as it is either cancelled, inactive, or sold out.', 'danger')
        return redirect(url_for('main.eventDetails', event_id=event.id))

    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('name')
        last_name = request.form.get('lastname')
        quantity = int(request.form.get('quantity'))

        # Check if quantity is valid and does not exceed available tickets
        if quantity <= 0:
            flash('Quantity must be greater than 0', 'danger')
            return redirect(url_for('main.purchase_tickets', event_id=event_id))
        elif quantity > event.ticket_amount:
            flash(f'Only {event.ticket_amount} tickets are available.', 'danger')
            return redirect(url_for('main.purchase_tickets', event_id=event_id))

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

        # Update the ticket amount
        event.ticket_amount -= quantity

        # Check if event should be marked as sold out
        if event.ticket_amount <= 0:
            event.status = 'Sold Out'

        # Save the order and event status in the database
        db.session.add(new_order)
        db.session.commit()

        # Redirect to confirmation page with the new order ID
        return redirect(url_for('main.confirmation', order_id=new_order.id))

    return render_template('purchaseTickets.html', event=event)

@main_bp.route('/confirmation/<int:order_id>')
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
        'artist_name': event.artist.name,
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

@main_bp.route('/findEvents')
def findEvents():
    # Get the selected genre from the query parameter (if any)
    genre = request.args.get('genre')

    # Define the main genres
    main_genres = ['Pop', 'Jazz', 'Rock', 'Classical', 'Electronic', 'Indie']

    # Filtering logic
    if genre:
        if genre == "Other":
            # Show events with genres not in the main list
            events = Event.query.filter(~Event.genre.in_(main_genres)).all()
        else:
            # Show events matching the selected genre
            events = Event.query.filter_by(genre=genre).all()
    else:
        # If no genre is selected, show all events
        events = Event.query.all()

    genres = main_genres + ['Other']  # Add 'Other' as a category
    return render_template('findEvents.html', events=events, genres=genres)

@main_bp.route('/show-events')
def show_events():
    events = Event.query.all()
    event_list = [f"ID: {event.id}, Name: {event.event_name}" for event in events]
    return "<br>".join(event_list)

@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@main_bp.route('/trigger-500')
def trigger_500():
    # Deliberately raise an exception to trigger a 500 error
    raise Exception("This is a test 500 error!")

@main_bp.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    # Retrieve the event by ID
    event = Event.query.get_or_404(event_id)
    
    # Ensure the current user is the owner of the event
    if event.owner_id != current_user.id:
        flash('You do not have permission to edit this event.', 'danger')
        return redirect(url_for('main.BookingHistory'))
    
    if request.method == 'POST':
        # Get form data from the request
        event_name = request.form.get('eventName').strip()
        artist_name = request.form.get('artistName').strip()
        venue = request.form.get('venue').strip()
        description = request.form.get('description').strip()
        date_str = request.form.get('date').strip()  # Get date as string from form
        start_time_str = request.form.get('startTime').strip()
        end_time_str = request.form.get('endTime').strip()
        price_str = request.form.get('price').strip()
        ticket_amount_str = request.form.get('tickets').strip()
        genre = request.form.get('genre').strip()  # Get genre from the form

        # Validate required fields
        if not all([event_name, artist_name, venue, description, date_str, start_time_str, end_time_str, price_str, ticket_amount_str, genre]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.edit_event', event_id=event_id))
        
        # Convert date and time to Python objects (using DD/MM/YYYY format for the date)
        try:
            event_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format. Please use DD/MM/YYYY for date and HH:MM for time.', 'danger')
            return redirect(url_for('main.edit_event', event_id=event_id))
        
        # Validate and convert price and ticket_amount
        try:
            price = float(price_str)
            ticket_amount = int(ticket_amount_str)
            if price < 0:
                raise ValueError("Price cannot be negative.")
            if ticket_amount < 1:
                raise ValueError("Ticket amount must be at least 1.")
        except ValueError as ve:
            flash(f'Invalid input for price or ticket amount: {ve}', 'danger')
            return redirect(url_for('main.edit_event', event_id=event_id))
        
        # Find the artist by name
        artist = Artist.query.filter_by(name=artist_name).first()
        if not artist:
            flash(f"Artist '{artist_name}' not found.", 'danger')
            return redirect(url_for('main.edit_event', event_id=event_id))
        
        # Handle image upload
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(image.filename)

            # Get the absolute path for the uploads folder
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            image_path = os.path.join(upload_folder, filename)
            try:
                image.save(image_path)
                event.image_path = f'uploads/{filename}'
            except Exception as e:
                flash('Failed to upload image. Please try again.', 'danger')
                current_app.logger.error(f"Image upload error: {e}")
                return redirect(url_for('main.edit_event', event_id=event_id))
        
        # Update event details
        event.event_name = event_name
        event.artist_id = artist.id
        event.venue = venue
        event.description = description
        event.date = event_date
        event.start_time = start_time
        event.end_time = end_time
        event.price = price
        event.ticket_amount = ticket_amount
        event.genre = genre

        # Update event status based on new date and ticket amount
        event.update_status()
        
        # Commit changes to the database
        try:
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('main.BookingHistory'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the event. Please try again.', 'danger')
            current_app.logger.error(f"Error updating event: {e}")
            return redirect(url_for('main.edit_event', event_id=event_id))
    
    # For GET request, render the edit form with current event data
    return render_template('EditEvent.html', event=event)