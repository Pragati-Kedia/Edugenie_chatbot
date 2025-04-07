from flask import Flask, request, jsonify
import PyPDF2
import difflib
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Predefined common chatbot questions and answers
predefined_answers = {
    "hello": "Hello! How can I assist you today?",
    "hi": "Hi there! What can I help you with?",
    "how are you?": "I'm just a bot, but I'm here to help!",
    "who are you?": "I'm a chatbot that can answer your questions.",
    "what can you do?": "I can answer questions based on my knowledge and the PDF you provided.",
    "thank you": "You're welcome!",
    "bye": "Goodbye! Have a great day!",
    "exit": "Goodbye! Hope to assist you again."
}

# Load and extract text from the PDF file
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    except FileNotFoundError:
        print("Error: PDF file not found. Please check the file path.")
        return ""

# Clean text for matching
def clean_text(text):
    text = text.lower()
    text = re.sub(f"[{string.punctuation}]", "", text)
    return text

# Load Q&A from PDF
PDF_PATH = "C:/Users/abc/Downloads/Edunew (1).pdf"
qa_text = extract_text_from_pdf(PDF_PATH)

qa_dict = {}
questions_list = []
answers_list = []

if qa_text:
    qa_pairs = qa_text.split("Q:")
    for pair in qa_pairs[1:]:
        parts = pair.split("A:")
        if len(parts) == 2:
            question = clean_text(parts[0].strip())
            answer = parts[1].strip()
            qa_dict[question] = answer
            questions_list.append(question)
            answers_list.append(answer)

    vectorizer = TfidfVectorizer()
    question_vectors = vectorizer.fit_transform(questions_list)

# Find best matches
def get_best_matches(user_query, top_n=3):
    user_query_clean = clean_text(user_query)

    if user_query_clean in predefined_answers:
        return [{"type": "predefined", "question": user_query, "answer": predefined_answers[user_query_clean]}]

    query_vector = vectorizer.transform([user_query_clean])
    similarity_scores = cosine_similarity(query_vector, question_vectors).flatten()

    top_indices = similarity_scores.argsort()[-top_n:][::-1]
    top_matches = [
        {
            "type": "pdf",
            "question": questions_list[i],
            "answer": answers_list[i],
            "score": float(similarity_scores[i])
        }
        for i in top_indices
    ]

    if top_matches[0]["score"] > 0.2:
        return top_matches
    else:
        return [{"type": "no_match", "question": user_query, "answer": "Sorry, I couldn't find an answer to that question."}]

# Route to ask question
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    user_input = data.get("question", "")

    if not user_input:
        return jsonify({"error": "Please provide a valid question."}), 400

    results = get_best_matches(user_input)

    if results[0]["type"] == "predefined":
        return jsonify({
            "response_type": "predefined",
            "answer": results[0]["answer"]
        })

    elif results[0]["type"] == "no_match":
        return jsonify({
            "response_type": "no_match",
            "answer": results[0]["answer"]
        })

    else:
        suggestions = [res["question"] for res in results]
        return jsonify({
            "response_type": "suggestions",
            "original_question": user_input,
            "suggestions": suggestions,
            "prompt": "Select the most relevant question (1/2/3):"
        })


# Run app
if __name__ == "__main__":
    if not qa_text:
        print("PDF data not loaded. Exiting.")
    else:
        app.run(debug=True)
