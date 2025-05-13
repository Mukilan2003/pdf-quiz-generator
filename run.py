from app import create_app

# Create the Flask application instance - this is what Gunicorn will use
app = create_app()

# DO NOT include any code here that requires an application context
# All setup that requires app context should be in app/__init__.py

if __name__ == '__main__':
    # This block only runs when you execute this file directly (not via Gunicorn)
    app.run(debug=True)
