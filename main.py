from data import update_used_words_if_needed, load_word_list
from helpers import get_user_input
from logic import exclude_used_words, rank_words_by_scrabble_score, create_game_state


def main():
    # Update and load word lists
    update_used_words_if_needed('used_words.txt')
    word_list = load_word_list('wordlist.txt')
    used_words = load_word_list('used_words.txt')
    filtered_words = exclude_used_words(word_list, used_words)

    # Load fallback word list
    fallback_words = load_word_list('wordle_possibles.txt')

    # Create game state with fallback words
    game_state = create_game_state(filtered_words, fallback_words)
    guess_count = 1

    while True:
        print(f"\n--- Guess #{guess_count} ---")
        word_count = game_state.get_word_count()
        print(f"Possible words left: {word_count}")

        if game_state.is_using_fallback():
            print("Note: Using extended word list due to no matches in primary list")

        if word_count == 1:
            final_word = game_state.get_possible_words()[0]
            print(f"The word is: {final_word}")
            break
        elif word_count == 0:
            print("No words left matching the feedback. Something went wrong!")
            break

        # Show ranked preview of possible words
        possible_words = game_state.get_possible_words()
        ranked_preview = rank_words_by_scrabble_score(possible_words)[:10]  # Show top 10
        print(f"Top suggested words: {ranked_preview}")

        # Get user input
        guess, feedback = get_user_input()
        game_state.add_guess(guess, feedback)

        # Show history
        print("\nGuess History:")
        for guess_info in game_state.get_history():
            print(f"Guess: {guess_info['guess']}, Feedback: {guess_info['feedback']}")

        guess_count += 1


if __name__ == "__main__":
    main()
