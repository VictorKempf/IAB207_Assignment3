from website import create_app, db

# Create the Flask app instance
app = create_app()

# Ensure tables are created if they don't exist yet
with app.app_context():
    db.create_all()  # This will create the tables

if __name__ == '__main__':
    app.run(debug=True)
