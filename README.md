# PDF Quiz Generator

A web application that uses Google's Gemini Flash 2.0 API to extract text from PDFs, generate summaries, and create interactive quizzes.

## Features

- PDF text extraction using PyPDF2
- Content summarization with Gemini Flash 2.0
- Generation of summary PDFs
- Interactive MCQ quiz generation based on PDF content
- Customizable quiz difficulty and topic focus
- Animated UI for quiz taking
- Detailed results and performance analysis
- Google OAuth authentication

## Local Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pdf_quiz_generator.git
   cd pdf_quiz_generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the `.env.example` file:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file and add your:
   - Gemini API key
   - Secret key for Flask
   - Google OAuth credentials (client ID and client secret)

## Usage

1. Run the application:
   ```
   python run.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

3. Sign in with Google

4. Upload a PDF file

5. Generate a summary of the PDF content

6. Configure and generate a quiz based on the PDF

7. Take the quiz and view your results

## Deployment to Render

1. Create a Render account at https://render.com if you don't have one.

2. Create a new Web Service:
   - Connect your GitHub repository
   - Select the repository containing your PDF Quiz Generator application
   - Configure the service:
     - Name: pdf-quiz-generator (or your preferred name)
     - Environment: Python
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn render_app:app`

3. Add environment variables in the Render dashboard:
   - SECRET_KEY (generate a secure random string)
   - GEMINI_API_KEY (your Google Gemini API key)
   - GOOGLE_CLIENT_ID (your Google OAuth client ID)
   - GOOGLE_CLIENT_SECRET (your Google OAuth client secret)
   - BASE_URL (your Render application URL, e.g., https://pdf-quiz-generator.onrender.com)
   - RENDER=true

4. Deploy the application.

### Google OAuth Configuration for Render

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project
3. Navigate to APIs & Services > Credentials
4. Edit your OAuth 2.0 Client ID
5. Add your Render application URL to the Authorized JavaScript origins
6. Add `https://your-render-app.onrender.com/auth/google-callback` to the Authorized redirect URIs
7. Save the changes

## Deployment to Vercel

1. Create a Vercel account at https://vercel.com if you don't have one.

2. Install the Vercel CLI (optional):
   ```
   npm install -g vercel
   ```

3. Create a new project in Vercel:
   - Connect your GitHub repository
   - Select the repository containing your PDF Quiz Generator application
   - Configure the project:
     - Framework Preset: Other
     - Root Directory: ./
     - Build Command: pip install -r requirements.txt
     - Output Directory: (leave default)

4. Add environment variables in the Vercel dashboard:
   - SECRET_KEY (generate a secure random string)
   - GEMINI_API_KEY (your Google Gemini API key)
   - GOOGLE_CLIENT_ID (your Google OAuth client ID)
   - GOOGLE_CLIENT_SECRET (your Google OAuth client secret)
   - BASE_URL (your Vercel application URL, e.g., https://pdf-quiz-generator.vercel.app)
   - VERCEL=true

5. Deploy the application.

### Google OAuth Configuration for Vercel

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project
3. Navigate to APIs & Services > Credentials
4. Edit your OAuth 2.0 Client ID
5. Add your Vercel application URL to the Authorized JavaScript origins
6. Add `https://your-vercel-app.vercel.app/auth/google-callback` to the Authorized redirect URIs
7. Save the changes

## Project Structure

```
pdf_quiz_generator/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── uploads/
│   ├── templates/
│   ├── __init__.py
│   ├── routes.py
│   └── utils/
│       ├── __init__.py
│       ├── pdf_processor.py
│       └── quiz_generator.py
├── config.py
├── requirements.txt
└── run.py
```

## Technologies Used

- Flask: Web framework
- PyPDF2: PDF text extraction
- Google Generative AI (Gemini Flash 2.0): Text summarization and quiz generation
- ReportLab: PDF generation
- Bootstrap: Frontend styling
- Chart.js: Data visualization
- Animate.css: UI animations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Google Generative AI for providing the Gemini Flash 2.0 API
- The Flask team for the excellent web framework
- All open-source libraries used in this project
