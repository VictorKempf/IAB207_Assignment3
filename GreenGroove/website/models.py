from . import db
from datetime import datetime
from flask_login import UserMixin

# Define the User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    orders = db.relationship('Order', back_populates='user')
    comments = db.relationship('Comment', backref='user')
    events = db.relationship('Event', backref='owner')

    def __repr__(self):
        return f"<User {self.email} ID {self.id}>"
    
# Define the Event model
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), unique=True, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    ticket_amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')  # Example: status can be 'Open', 'Cancelled', etc.
    genre = db.Column(db.String(50), nullable=False)  # New genre field

    artist = db.relationship('Artist', back_populates='events')
    orders = db.relationship('Order', back_populates='event')
    comments = db.relationship('Comment', backref='event')

     # Status constants
    OPEN = "Open"
    INACTIVE = "Inactive"
    SOLD_OUT = "Sold Out"
    CANCELLED = "Cancelled"

    def update_status(self):
        if self.status != Event.CANCELLED:  # Don't update if manually cancelled
            today = datetime.now().date()
            if self.date < today:
                self.status = Event.INACTIVE  # Set to 'Inactive' if the date is in the past
            elif self.ticket_amount <= 0:
                self.status = Event.SOLD_OUT  # Set to 'Sold Out' if no tickets are available
            else:
                self.status = Event.OPEN  # Set to 'Open' if tickets are available and date is in the future


    def __repr__(self):
        return f"<Event {self.event_name}>"

# Define the Comment model
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id}>"

# Define the Order model
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    event = db.relationship('Event', back_populates='orders')

    def __repr__(self):
        return f"<Order {self.order_id} by User {self.user_id}>"

# Define the Artist model
class Artist(db.Model):
    __tablename__ = 'artists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    
    events = db.relationship('Event', back_populates='artist', lazy=True)

    def __repr__(self):
        return f"<Artist {self.name}>"
