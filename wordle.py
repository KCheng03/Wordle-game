import random

# Max rounds before game over
max_attempts = 6

# List of 5-letter words (you can expand this list)
word_list = [
    "apple", "brave", "crane", "dwarf", "eagle",
    "flame", "grape", "house", "index", "jolly",
    "knife", "lemon", "mango", "night", "ocean",
    "party", "queen", "roast", "stone", "trust",
    "urban", "vigor", "waltz", "xenon", "yacht", "zebra"
]

def get_feedback(guess, secret):
    feedback = [''] * 5
    secret_chars = list(secret)
    guess_chars = list(guess)

    # First pass: check for correct letters in correct position
    for i in range(5):
        if guess_chars[i] == secret_chars[i]:
            feedback[i] = '🟩'  # Green
            secret_chars[i] = None  # Mark as used
            guess_chars[i] = None
        else:
            feedback[i] = None

    # Second pass: check for correct letters in wrong position
    for i in range(5):
        if guess_chars[i] is not None:
            if guess_chars[i] in secret_chars:
                feedback[i] = '🟨'  # Orange
                secret_index = secret_chars.index(guess_chars[i])
                secret_chars[secret_index] = None  # Mark as used
            else:
                feedback[i] = '⬜'  # White

    return ''.join(feedback)

def main():
    secret_word = random.choice(word_list)
    attempts = max_attempts

    print("Welcome to Wordle!")
    print("Guess the 5-letter word. You have 6 attempts.\n")

    for attempt in range(1, attempts + 1):
        while True:
            guess = input(f"Attempt {attempt}: ").lower()
            if len(guess) != 5:
                print("Please enter a 5-letter word.")
            elif guess not in word_list:
                print("Word not in list. Try again.")
            else:
                break

        feedback = get_feedback(guess, secret_word)
        print(feedback)

        if guess == secret_word:
            print(f"Congratulations! You guessed the word '{secret_word}' in {attempt} attempts.")
            break
    else:
        print(f"Game over! The word was '{secret_word}'.")

if __name__ == "__main__":
    main()