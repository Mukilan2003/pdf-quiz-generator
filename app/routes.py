from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from app.utils.pdf_processor import extract_text_from_pdf, generate_summary_pdf, create_pdf_summary
from app.utils.quiz_generator import generate_quiz
from app.middleware import login_required
from app.utils.firebase_integration import FirebaseIntegration

firebase = FirebaseIntegration()

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['pdf_file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{original_filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text from PDF
        pdf_text = extract_text_from_pdf(file_path)

        # Store in session
        session['pdf_path'] = file_path
        session['pdf_text'] = pdf_text
        session['original_filename'] = original_filename

        return redirect(url_for('main.summarize'))

    flash('Invalid file type. Please upload a PDF.')
    return redirect(url_for('main.index'))

@main.route('/summarize')
@login_required
def summarize():
    if 'pdf_text' not in session:
        flash('Please upload a PDF first')
        return redirect(url_for('main.index'))

    return render_template('summarize.html', filename=session.get('original_filename'))

@main.route('/generate-summary', methods=['POST'])
@login_required
def generate_summary():
    if 'pdf_text' not in session:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_text = session.get('pdf_text')

    # Generate summary using Gemini API
    summary = create_pdf_summary(pdf_text)

    # Generate a PDF with the summary
    summary_pdf_path = generate_summary_pdf(summary, session.get('original_filename'))

    # Store in session
    session['summary'] = summary
    session['summary_pdf_path'] = summary_pdf_path

    return jsonify({'success': True, 'redirect': url_for('main.quiz_setup')})

@main.route('/quiz-setup')
@login_required
def quiz_setup():
    if 'summary' not in session:
        flash('Please generate a summary first')
        return redirect(url_for('main.index'))

    return render_template('quiz_setup.html', summary=session.get('summary'))

@main.route('/generate-quiz', methods=['POST'])
@login_required
def create_quiz():
    if 'pdf_text' not in session:
        return jsonify({'error': 'No PDF uploaded'}), 400

    difficulty = request.form.get('difficulty', 'medium')
    topics = request.form.get('topics', '').split(',')
    topics = [topic.strip() for topic in topics if topic.strip()]

    # Generate quiz questions
    quiz = generate_quiz(session.get('pdf_text'), difficulty, topics)

    # Store in session
    session['quiz'] = quiz
    session['current_question'] = 0
    session['answers'] = []

    return jsonify({'success': True, 'redirect': url_for('main.quiz')})

@main.route('/quiz')
@login_required
def quiz():
    if 'quiz' not in session:
        flash('Please set up a quiz first')
        return redirect(url_for('main.index'))

    quiz = session.get('quiz')
    current_q = session.get('current_question', 0)

    if current_q >= len(quiz):
        return redirect(url_for('main.results'))

    question = quiz[current_q]
    return render_template('quiz.html', question=question, question_number=current_q+1, total_questions=len(quiz))

@main.route('/submit-answer', methods=['POST'])
@login_required
def submit_answer():
    if 'quiz' not in session:
        return jsonify({'error': 'No active quiz'}), 400

    answer = request.form.get('answer')
    current_q = session.get('current_question', 0)
    quiz = session.get('quiz')

    if current_q >= len(quiz):
        return jsonify({'redirect': url_for('main.results')})

    # Record answer
    answers = session.get('answers', [])
    answers.append({
        'question_number': current_q + 1,
        'selected_answer': answer,
        'correct_answer': quiz[current_q]['correct_answer'],
        'is_correct': answer == quiz[current_q]['correct_answer']
    })
    session['answers'] = answers

    # Move to next question
    session['current_question'] = current_q + 1

    if current_q + 1 >= len(quiz):
        return jsonify({'redirect': url_for('main.results')})
    else:
        return jsonify({'redirect': url_for('main.quiz')})

@main.route('/results')
@login_required
def results():
    if 'answers' not in session:
        flash('No quiz results available')
        return redirect(url_for('main.index'))

    answers = session.get('answers', [])
    correct_count = sum(1 for answer in answers if answer.get('is_correct'))
    total_questions = len(answers)
    score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    return render_template('results.html',
                          answers=answers,
                          correct_count=correct_count,
                          total_questions=total_questions,
                          score_percentage=score_percentage)

@main.route('/download-summary')
@login_required
def download_summary():
    if 'summary_pdf_path' not in session:
        flash('No summary available to download')
        return redirect(url_for('main.index'))

    return send_file(session.get('summary_pdf_path'), as_attachment=True,
                    download_name=f"Summary_{session.get('original_filename', 'document.pdf')}")

@main.route('/reset')
def reset():
    # Clear session data
    session.clear()
    return redirect(url_for('main.index'))
