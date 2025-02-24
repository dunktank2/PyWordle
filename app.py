import json

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session  # For server-side session handling (optional for larger apps)
from data import update_used_words_if_needed, load_word_list
from logic import filter_words, exclude_used_words, rank_words_by_scrabble_score

app = Flask(__name__)

# Set up secret key and session config
app.secret_key = "Q2q&Xho9qs!I#67!"  # Replace with a secure random key
app.config["SESSION_TYPE"] = "filesystem"  # Storing sessions on the filesystem
Session(app)

@app.route("/")
def home():
    """Serve the main webpage."""
    # Reset guess counter and filtered words when visiting the page
    session.clear()
    session["guess_count"] = 0
    session["history"] = []  # Initialize an empty history

    # Ensure `used_words` and `word_list` are up-to-date
    update_used_words_if_needed('used_words.txt')
    word_list = load_word_list('wordlist.txt')
    used_words = load_word_list('used_words.txt')
    session["word_list"] = exclude_used_words(word_list, used_words)

    return render_template("index.html")  # Your frontend HTML file


@app.route("/filter_words", methods=["POST"])
def filter_words_api():
    """API endpoint to filter words based on guess and feedback."""
    # Get the current state of possible words from the session
    if "possible_words" not in session:
        session["possible_words"] = session["word_list"]

    data = request.get_json()
    guess = data["guess"].strip().lower()
    feedback = data["feedback"].strip().upper()

    # Filter the words based on the guess and feedback
    possible_words = session["possible_words"]
    filtered_words = filter_words(possible_words, guess, feedback)

    # Update session with the new filtered words
    session["possible_words"] = filtered_words
    session["guess_count"] += 1

    # Add the current guess and feedback to the history
    session["history"].append({"guess": guess, "feedback": feedback})

    # Check if only one word is left
    if len(filtered_words) == 1:
        final_word = filtered_words[0]
        if final_word != guess:
            # Return both the guess and the final answer when only one word is left
            response_json = jsonify({
                "final_answer": {"guess": guess, "feedback": feedback, "final_word": final_word},
                "history": session["history"],
                "ranked_words": []  # No possible words left to show
            })
            return response_json
        else:
            # Return the guess as the final answer when it is the only word left
            response_json = jsonify({
                "final_answer": {"guess": guess, "feedback": feedback, "final_word": guess},
                "history": session["history"],
                "ranked_words": []  # No possible words left to show
            })
            return response_json
    elif len(filtered_words) == 0:
        # Edge case: No words match the rules
        response_json = jsonify({
            "final_answer": {"guess": guess, "feedback": feedback, "final_word": "Invalid"},
            "history": session["history"],
            "ranked_words": []
        })
        return response_json
    else:
        # Return ranked possible words and history as usual
        ranked_preview = rank_words_by_scrabble_score(filtered_words)
        response_json = jsonify({
            "ranked_words": ranked_preview,
            "history": session["history"]
        })
        return response_json


if __name__ == "__main__":
    app.run(debug=True)
