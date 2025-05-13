from app import create_app

# Create the Flask application instance
app = create_app()

# This ensures the application context is properly set up
# when running with Gunicorn
application = app  # For WSGI compatibility

if __name__ == '__main__':
    app.run()
