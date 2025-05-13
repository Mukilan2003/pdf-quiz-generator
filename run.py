from app import create_app
import os

# Create the Flask application instance
app = create_app()

# Push an application context so that app.config can be accessed
with app.app_context():
    # Ensure upload directory exists
    if not os.environ.get('RENDER'):
        # Only create this directory locally, not on Render
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True)
