import google.generativeai as genai
from flask import current_app
import os

def generate_quiz(pdf_text, difficulty='medium', topics=None):
    """
    Generate quiz questions based on PDF content.

    Args:
        pdf_text (str): The text extracted from the PDF
        difficulty (str): The difficulty level ('easy', 'medium', 'hard')
        topics (list): List of specific topics to focus on

    Returns:
        list: A list of question dictionaries
    """
    # Get API key from environment variable
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        api_key = current_app.config.get('GEMINI_API_KEY')

    # Remove quotes if present
    if api_key and api_key.startswith("'") and api_key.endswith("'"):
        api_key = api_key[1:-1]

    # Configure the Gemini API
    genai.configure(api_key=api_key)

    # Set up the model
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prepare the topics string
    topics_str = ", ".join(topics) if topics and len(topics) > 0 else "all relevant topics"

    # Generate the prompt based on difficulty and topics
    prompt = f"""
    Based on the following text from a PDF document, generate 10 multiple-choice questions (MCQs).

    Difficulty level: {difficulty}

    Topics to focus on: {topics_str}

    For each question:
    1. Create a clear, concise question
    2. Provide exactly 4 answer options (A, B, C, D)
    3. Indicate which option is correct
    4. Include a brief explanation of why the answer is correct

    Format the output as a JSON array of objects with the following structure:
    [
      {{
        "question": "Question text here?",
        "options": ["A. Option A", "B. Option B", "C. Option C", "D. Option D"],
        "correct_answer": "A. Option A",
        "explanation": "Explanation of why Option A is correct"
      }},
      ...
    ]

    TEXT:
    {pdf_text[:100000]}  # Limiting text length to avoid token limits
    """

    try:
        # Generate the questions
        response = model.generate_content(prompt)

        # Parse the JSON response
        import json
        import re

        # Clean up the response text to extract just the JSON part
        response_text = response.text
        # Find JSON array pattern
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            questions = json.loads(json_str)
        else:
            # Fallback if regex doesn't work
            # Remove any text before the first '[' and after the last ']'
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                questions = json.loads(json_str)
            else:
                # If still can't parse, create a default structure
                questions = []
                for i in range(10):
                    questions.append({
                        "question": f"Question {i+1} (Error parsing model response)",
                        "options": [f"A. Option A", f"B. Option B", f"C. Option C", f"D. Option D"],
                        "correct_answer": "A. Option A",
                        "explanation": "Error parsing model response"
                    })

        return questions

    except Exception as e:
        print(f"Error parsing quiz questions: {e}")
        # Return a default set of questions if parsing fails
        return [
            {
                "question": f"Question {i+1} (Error generating questions)",
                "options": [f"A. Option A", f"B. Option B", f"C. Option C", f"D. Option D"],
                "correct_answer": "A. Option A",
                "explanation": "Error generating questions"
            } for i in range(10)
        ]
