from flask import Flask, request, jsonify, render_template
import json
import random

app = Flask(__name__)

# Load the question bank at the start
with open("questions.json", "r") as file:
    QUESTION_BANK = json.load(file)

# Memory
CURRENT_EXAM = []
CURRENT_QUESTION_INDEX = 0
USER_ANSWERS = []
ASKED_QUESTION_IDS = set()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    global CURRENT_EXAM, CURRENT_QUESTION_INDEX, USER_ANSWERS, ASKED_QUESTION_IDS

    data = request.get_json()
    user_input = data.get('message', '').strip().lower()

    if user_input == "Start" or "start":
        # Filter out used questions
        unused_questions = [q for q in QUESTION_BANK if q["id"] not in ASKED_QUESTION_IDS]

        # If not enough unused questions, allow reuse but prefer unused
        if len(unused_questions) < 15:
            combined_pool = QUESTION_BANK.copy()
            random.shuffle(combined_pool)
            CURRENT_EXAM = random.sample(combined_pool, 15)
            ASKED_QUESTION_IDS.clear()
        else:
            CURRENT_EXAM = random.sample(unused_questions, 15)

        CURRENT_QUESTION_INDEX = 0
        USER_ANSWERS.clear()

        # Track used IDs
        for q in CURRENT_EXAM:
            ASKED_QUESTION_IDS.add(q["id"])

        reply = format_question(CURRENT_EXAM[CURRENT_QUESTION_INDEX], CURRENT_QUESTION_INDEX + 1)
        return jsonify({"reply": reply})

    elif user_input in ["a", "b", "c", "d"]:
        if CURRENT_EXAM and CURRENT_QUESTION_INDEX < len(CURRENT_EXAM):
            question = CURRENT_EXAM[CURRENT_QUESTION_INDEX]
            correct = question["answer"]

            # Convert to list for multiple correct support
            if not isinstance(correct, list):
                correct = [correct]

            is_correct = user_input.upper() in correct
            explanation = question.get("explanation", "")
            USER_ANSWERS.append({
                "question": question["question"],
                "user_input": user_input.upper(),
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": explanation
            })

            feedback = "✅ Correct!" if is_correct else f"❌ Incorrect. The correct answer(s): {', '.join(correct)}"
            if explanation:
                feedback += f"\n\nℹ️ {explanation}"

            CURRENT_QUESTION_INDEX += 1

            if CURRENT_QUESTION_INDEX < len(CURRENT_EXAM):
                next_question = format_question(CURRENT_EXAM[CURRENT_QUESTION_INDEX], CURRENT_QUESTION_INDEX + 1)
                return jsonify({"reply": f"{feedback}\n\n{next_question}"})
            else:
                score = sum(1 for ans in USER_ANSWERS if ans["is_correct"])
                final_feedback = [f"📝 Exam complete! You got {score} out of {len(USER_ANSWERS)} correct."]
                for i, ans in enumerate(USER_ANSWERS, 1):
                    result = "✅" if ans["is_correct"] else "❌"
                    explain = f" - {ans['explanation']}" if ans["explanation"] else ""
                    correct_choices = ", ".join(ans["correct_answer"])
                    final_feedback.append(f"{result} Q{i}: {ans['question']}\nYour Answer: {ans['user_input']}\nCorrect: {correct_choices}{explain}")
                return jsonify({"reply": "\n\n".join(final_feedback)})

    return jsonify({"reply": "❓ Hmm, I don't recognise you're answer. Please type 'Start' to begin an new mock, or answer using A, B, C, or D to answer the question."})


def format_question(q, number):
    # Get correct answer's text
    correct_letter = q["answer"]
    correct_option = q["options"][ord(correct_letter.upper()) - 65]

    # Shuffle the options
    shuffled_options = q["options"].copy()
    random.shuffle(shuffled_options)

    # Determine the new correct answer letter
    new_index = shuffled_options.index(correct_option)
    q["options"] = shuffled_options
    q["answer"] = chr(65 + new_index)

    # Build option list
    options_text = ""
    for i, opt in enumerate(shuffled_options):
        options_text += f"{chr(65+i)}: {opt}\n"

    return f"✅ Question {number} (ID #{q['id']}):\n{q['question']}\n\n{options_text}\nPlease choose either A, B, C, or D."



if __name__ == "__main__":
    app.run(debug=True)