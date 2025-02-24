# Prompt the user for input
def get_user_input():
    """Prompt the user for a guess and feedback."""
    guess = input("Enter your guess (e.g., 'apple'): ").strip().lower()

    while True:
        feedback = input("Enter the feedback (e.g., 'GBBBB'): ").strip().upper()
        if len(feedback) == 5 and all(c in 'GBY' for c in feedback):
            break
        print("Invalid feedback format. Use 'G', 'B', 'Y' only and ensure it's 5 characters long.")

    return guess, feedback
