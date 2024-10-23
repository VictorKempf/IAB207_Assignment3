from datetime import datetime
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from .models import Order, Event, User, db


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/createEvent')
def createEvent():
    return render_template('createEvent.html')

@main_bp.route('/BookingHistory')
def BookingHistory():
    # Fetch the current user's orders
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('bookingHistory.html', orders=orders)

@main_bp.route('/eventDetails')
def eventDetails():
    return render_template('eventDetails.html')


@main_bp.route('/purchaseTickets', methods=['GET', 'POST'])
def purchaseTickets():
    event_id = request.args.get('event_id')
    quantity = request.form.get('quantity', default=1, type=int)
    
    # Get the event details from the database
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        # Create a new order
        total_price = event.price * quantity
        new_order = Order(
            order_id=f"ORD{int(datetime.utcnow().timestamp())}",  # Unique order ID
            user_id=current_user.id,  # Link to the logged-in user
            event_id=event.id,  # Link to the event
            quantity=quantity,
            total_price=total_price,
            booking_date=datetime.now()  # Set booking date
        )

        # Add the order to the database
        db.session.add(new_order)
        db.session.commit()  # Commit the transaction to save the order

        # Redirect to the booking history or a confirmation page
        return redirect(url_for('main.booking_history'))
    
    return render_template('purchaseTickets.html', event=event, quantity=quantity)


@main_bp.route('/confirmation/<int:order_id>')
def confirmation_page(order_id):
    # Get the order details from the database
    order = Order.query.get_or_404(order_id)
    event = Event.query.get_or_404(order.event_id)

    return render_template('confirmation.html', order=order, event=event)
