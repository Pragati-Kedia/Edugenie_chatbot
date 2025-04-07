from flask import Flask, request, jsonify
import PyPDF2
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

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
def extract_text_from_pdf(pdf_path):
   try:
       with open(pdf_path, "rb") as file:
           reader = PyPDF2.PdfReader(file)
           text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
       return text
   except FileNotFoundError:
       return ""
def clean_text(text):
   text = text.lower()
   text = re.sub(f"[{string.punctuation}]", "", text)
   return text
PDF_PATH = r"D:/Edugenie-chatbot/qsnanspdf/Edunew.pdf"
qa_text = extract_text_from_pdf(PDF_PATH)
qa_dict = {}
questions_list = []
answers_list = []
vectorizer = TfidfVectorizer()
question_vectors = None
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
   if questions_list:
       question_vectors = vectorizer.fit_transform(questions_list)
def get_best_matches(user_query, top_n=3):
   user_query_clean = clean_text(user_query)
   # Check predefined responses first
   if user_query_clean in predefined_answers:
       return [(user_query_clean, predefined_answers[user_query_clean], 1.0)]
   if not question_vectors:
       return [("No data", "Sorry, no PDF data available.")]
   query_vector = vectorizer.transform([user_query_clean])
   similarity_scores = cosine_similarity(query_vector, question_vectors).flatten()
   top_indices = similarity_scores.argsort()[-top_n:][::-1]
   top_matches = [(questions_list[i], answers_list[i], similarity_scores[i]) for i in top_indices]
   return top_matches if top_matches[0][2] > 0.2 else [("No good match", "Sorry, I couldn't find an answer to that question.", 0)]
@app.route("/ask", methods=["POST"])
def ask():
   data = request.get_json()
   question = data.get("question", "")
   if not question:
       return jsonify({"error": "Please provide a valid question"}), 400
   matches = get_best_matches(question)
   response = {
       "matches": [{"question": q, "answer": a, "score": round(s, 2)} for q, a, s in matches]
   }
   return jsonify(response)
@app.route("/", methods=["GET"])
def home():
   return "Chatbot is up and running! Use /ask endpoint with POST method."
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)