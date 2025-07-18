import json
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from data import update_used_words_if_needed, load_word_list
from logic import filter_words, exclude_used_words, rank_words_by_scrabble_score, create_game_state

app = Flask(__name__)
app.secret_key = "Q2q&Xho9qs!I#67!"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def home():
    """Serve the main webpage."""
    session.clear()

    # Initialize word lists
    update_used_words_if_needed('used_words.txt')
    word_list = load_word_list('wordlist.txt')
    used_words = load_word_list('used_words.txt')
    filtered_words = exclude_used_words(word_list, used_words)

    # Load fallback word list
    fallback_words = load_word_list('wordle_possibles.txt')

    # Create new game state and store in session
    game_state = create_game_state(filtered_words, fallback_words)
    session["game_state"] = game_state

    return render_template("index.html")


@app.route("/filter_words", methods=["POST"])
def filter_words_api():
    """API endpoint to filter words based on guess and feedback."""
    # Get or initialize game state
    if "game_state" not in session:
        update_used_words_if_needed('used_words.txt')
        word_list = load_word_list('wordlist.txt')
        used_words = load_word_list('used_words.txt')
        filtered_words = exclude_used_words(word_list, used_words)
        fallback_words = load_word_list('wordle_possibilities.txt')
        session["game_state"] = create_game_state(filtered_words, fallback_words)

    game_state = session["game_state"]

    data = request.get_json()
    guess = data["guess"].strip().lower()
    feedback = data["feedback"].strip().upper()

    # Add the guess and update possible words
    game_state.add_guess(guess, feedback)

    # Get current possible words and history
    possible_words = game_state.get_possible_words()
    word_count = game_state.get_word_count()
    history = game_state.get_history()

    # Check results
    if word_count == 1:
        final_word = possible_words[0]
        response = {
            "final_answer": {
                "guess": guess,
                "feedback": feedback,
                "final_word": final_word
            },
            "history": history,
            "ranked_words": [],
            "using_fallback": game_state.is_using_fallback()
        }
    elif word_count == 0:
        response = {
            "final_answer": {
                "guess": guess,
                "feedback": feedback,
                "final_word": "Invalid"
            },
            "history": history,
            "ranked_words": [],
            "using_fallback": game_state.is_using_fallback()
        }
    else:
        ranked_preview = rank_words_by_scrabble_score(possible_words)[:10]
        response = {
            "ranked_words": ranked_preview,
            "history": history,
            "word_count": word_count,
            "using_fallback": game_state.is_using_fallback()
        }

    session["game_state"] = game_state
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
