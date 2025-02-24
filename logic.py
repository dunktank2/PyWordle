# Scrabble letter values
SCRABBLE_LETTER_VALUES = {
    'A': 1, 'E': 1, 'I': 1, 'O': 1, 'U': 1, 'L': 1, 'N': 1, 'S': 1, 'T': 1, 'R': 1,
    'D': 2, 'G': 2,
    'B': 3, 'C': 3, 'M': 3, 'P': 3,
    'F': 4, 'H': 4, 'V': 4, 'W': 4, 'Y': 4,
    'K': 5,
    'J': 8, 'X': 8,
    'Q': 10, 'Z': 10
}


def calculate_scrabble_score(word):
    """Calculate the Scrabble score of a given word."""
    return sum(SCRABBLE_LETTER_VALUES.get(char.upper(), 0) for char in word)


def rank_words_by_scrabble_score(words):
    """Rank words by their Scrabble score in ascending order."""
    return sorted(words, key=calculate_scrabble_score)


def filter_words(words, guess, feedback):
    """
    Filter the word list to only include words that match the feedback for the given guess.
    """
    filtered_words = []
    for word in words:
        if is_word_match(word, guess, feedback):
            filtered_words.append(word)
    return filtered_words


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

def exclude_used_words(all_words, used_words):
    return [word for word in all_words if word not in used_words]
