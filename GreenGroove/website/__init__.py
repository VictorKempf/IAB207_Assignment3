# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'
    app.secret_key = 'somesecretkey'
    Bootstrap4(app)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.scalar(db.select(User).where(User.id == user_id))

    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    # Create tables and populate test data if not already present
    with app.app_context():
        db.create_all()
        add_test_events_if_not_exist()

    return app

# Function to add test events if not already present
def add_test_events_if_not_exist():
    from .models import Event
    if Event.query.first() is None:
        add_test_events()  # Add test events if no events are present

def add_test_events():
    from datetime import datetime, time
    from .models import Event, db

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
            image_path="uploads/hoang-anh-nguy-n-lWDF2MsHaHg-unsplash.jpg",
            description="A night of smooth jazz with local artists.",
            genre="Jazz",
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
            image_path="uploads/adam-fugere-CR0B52XXfUs-unsplash.jpg",
            description="Rock out with Brisbane's best bands.",
            genre="Rock",
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
            image_path="uploads/manuel-nageli-NsgsQjHA1mM-unsplash.jpg",
            description="An evening of classical music featuring renowned orchestras.",
            genre="Classical",
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
            image_path="uploads/hanny-naibaho-aWXVxy8BSzc-unsplash.jpg",
            description="A full day of music performances featuring local and international artists.",
            genre="Festival",
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
            image_path="uploads/martin-robles-EKpByvjvioU-unsplash.jpg",
            description="A captivating theatre performance.",
            genre="Theatre",
            owner_id=1
        )
    ]

    for event in events:
        db.session.add(event)
    db.session.commit()
