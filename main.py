from data import update_used_words_if_needed, load_word_list, update_word_list_if_needed
from helpers import get_user_input
from logic import exclude_used_words, rank_words_by_scrabble_score, filter_words

def main():

    # Update the used words file if needed
    update_used_words_if_needed('used_words.txt')
    update_word_list_if_needed('word_list.txt')

    # Load the word list and used words list
    word_list = load_word_list('wordlist.txt')
    used_words = load_word_list('used_words.txt')

    # Exclude used words from the word list
    word_list = exclude_used_words(word_list, used_words)

    # Main word-guessing loop
    possible_words = word_list.copy()  # Start with the full filtered word list
    guess_count = 1

    while possible_words:
        print(f"--- Guess #{guess_count} ---")
        print(f"Possible words left: {len(possible_words)}")

        if len(possible_words) == 1:
            print(f"The word is: {possible_words[0]}")
            break

        # Print a preview of the top words (optional)
        ranked_preview = rank_words_by_scrabble_score(possible_words)
        print(f"Top ranked possible words: {ranked_preview}")

        # Get user input
        guess, feedback = get_user_input()

        # Filter the word list based on the guess and feedback
        possible_words = filter_words(possible_words, guess, feedback)

        if not possible_words:
            print("No words left matching the feedback. Exiting.")
            break

        guess_count += 1


if __name__ == "__main__":
    main()
