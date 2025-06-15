from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

def is_valid_age(age):
    return age.isdigit() and 0 < int(age) < 120

def is_valid_gender(gender):
    return gender.lower() in ['male', 'female', 'other']

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

@app.route('/')
def index():
    return render_template('appointment.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "").strip()
    session = request.json.get("session", {})

    next_question = ""
    error = None

    if "name" not in session:
        session["name"] = user_input
        next_question = "What is your age?"
    elif "age" not in session:
        if is_valid_age(user_input):
            session["age"] = user_input
            next_question = "What is your gender? Male, Female, or Other?"
        else:
            error = "Please provide a valid age between 1 and 120."
    elif "gender" not in session:
        if is_valid_gender(user_input):
            session["gender"] = user_input.lower()
            next_question = "Please tell me your 10-digit phone number."
        else:
            error = "Please say Male, Female, or Other."
    elif "phone" not in session:
        if is_valid_phone(user_input):
            session["phone"] = user_input
            next_question = "Briefly describe your medical problem."
        else:
            error = "Phone number must be 10 digits."
    elif "problem" not in session:
        session["problem"] = user_input
        return jsonify({
            "message": (
                f"Thank you, {session.get('name', '')}. Your appointment is booked.\n"
                f"Age: {session.get('age', '')}, Gender: {session.get('gender', '').capitalize()}, "
                f"Phone: {session.get('phone', '')}, Problem: {session.get('problem', '')}"
            ),
            "session": {},
            "done": True
        })

    return jsonify({
        "message": error if error else next_question,
        "session": session,
        "done": False
    })

if __name__ == '__main__':
    app.run(debug=True)