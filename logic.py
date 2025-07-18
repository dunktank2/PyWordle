# Scrabble letter values
SCRABBLE_LETTER_VALUES = {
    'A': 0.5, 'E': 0.5, 'I': 0.5, 'O': 0.75, 'U': 0.75, 'L': 1, 'N': 1, 'S': 1, 'T': 1, 'R': 1,
    'D': 2, 'G': 2,
    'B': 3, 'C': 3, 'M': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
    'K': 5,
    'J': 8, 'X': 8,
    'Q': 10, 'Z': 10
}


def calculate_scrabble_score(word):
    """Calculate the Scrabble score of a given word."""
    score = 0
    for char in word:
        score += (word.count(char) ** 2) * SCRABBLE_LETTER_VALUES.get(char.upper(), 0)
    return score


def rank_words_by_scrabble_score(words):
    """Rank words by their Scrabble score in ascending order."""
    return sorted(words, key=calculate_scrabble_score)


def is_word_match(word, guess, feedback):
    """
    Match a word against the guess and feedback considering duplicate letters properly.
    Green (G): Correct letter in the correct position.
    Yellow (Y): Correct letter in the wrong position.
    Black (B): Letter not in the word or already matched by other letters.
    """
    from collections import Counter

    word = list(word)  # Convert word to a list for mutable operations
    word_letter_counts = Counter(word)  # Count occurrences of each letter in the word

    # First pass: Process 'G' (Green)
    for i, (g_letter, fb) in enumerate(zip(guess, feedback)):
        if fb == 'G':
            if word[i] != g_letter:  # Green requires an exact match in position
                return False
            word_letter_counts[g_letter] -= 1  # Decrement count for the letter

    # Second pass: Process 'Y' and 'B'
    for i, (g_letter, fb) in enumerate(zip(guess, feedback)):
        if fb == 'Y':
            # Yellow requires the letter to be present but in a different position
            if g_letter not in word_letter_counts or word_letter_counts[g_letter] <= 0 or word[i] == g_letter:
                return False
            word_letter_counts[g_letter] -= 1  # Decrement count for the letter
        elif fb == 'B':
            # Black requires the letter NOT to appear (or already fully accounted for)
            if g_letter in word_letter_counts and word_letter_counts[g_letter] > 0:
                return False

    return True


def filter_words(words, guess, feedback):
    """
    Filter the word list to only include words that match the feedback for the given guess.
    """
    filtered_words = []
    for word in words:
        if is_word_match(word, guess, feedback):
            filtered_words.append(word)
    return filtered_words


def exclude_used_words(all_words, used_words):
    return [word for word in all_words if word not in used_words]


class WordleGameState:
    def __init__(self, initial_words, fallback_words=None):
        self.possible_words = initial_words.copy()
        self.fallback_words = fallback_words.copy() if fallback_words else None
        self.previous_guesses = []
        self.previous_feedback = []
        self.using_fallback = False

    def add_guess(self, guess, feedback):
        """Add a new guess and its feedback, then filter the possible words."""
        self.previous_guesses.append({"guess": guess, "feedback": feedback})
        filtered_words = filter_words(self.possible_words, guess, feedback)

        # If no words match and we have fallback words, switch to them
        if len(filtered_words) == 0 and self.fallback_words and not self.using_fallback:
            self.possible_words = self.fallback_words.copy()
            self.using_fallback = True
            # Reapply all previous guesses to the fallback list
            for guess_info in self.previous_guesses:
                self.possible_words = filter_words(self.possible_words,
                                                   guess_info["guess"],
                                                   guess_info["feedback"])
        else:
            self.possible_words = filtered_words

    def reset_with_new_words(self, new_words, fallback_words=None):
        """Reset with a new word list but maintain previous constraints."""
        self.possible_words = new_words.copy()
        self.fallback_words = fallback_words.copy() if fallback_words else None
        self.using_fallback = False
        # Apply all previous guesses and feedback
        for guess_info in self.previous_guesses:
            self.add_guess(guess_info["guess"], guess_info["feedback"])

    def get_possible_words(self):
        """Get the current list of possible words."""
        return self.possible_words.copy()

    def get_word_count(self):
        """Get the count of remaining possible words."""
        return len(self.possible_words)

    def get_history(self):
        """Get the history of guesses and feedback."""
        return self.previous_guesses

    def is_using_fallback(self):
        """Check if currently using fallback word list."""
        return self.using_fallback


def create_game_state(word_list, fallback_words=None):
    """Create a new game state with the given word list and optional fallback list."""
    return WordleGameState(word_list, fallback_words)
