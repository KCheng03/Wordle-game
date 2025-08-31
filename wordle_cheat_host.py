def get_feedback(guess, secret):
    feedback = [''] * 5
    secret_chars = list(secret)
    guess_chars = list(guess)

    # First pass: check for correct letters in correct position
    for i in range(5):
        if guess_chars[i] == secret_chars[i]:
            feedback[i] = '0'  # Green
            secret_chars[i] = None  # Mark as used
            guess_chars[i] = None
        else:
            feedback[i] = None

    # Second pass: check for correct letters in wrong position
    for i in range(5):
        if guess_chars[i] is not None:
            if guess_chars[i] in secret_chars:
                feedback[i] = '?'  # Orange
                secret_index = secret_chars.index(guess_chars[i])
                secret_chars[secret_index] = None  # Mark as used
            else:
                feedback[i] = '_'  # White

    return ''.join(feedback)

def filter_word_list(possible_words, guess):
    """
    Filter the word list as much as possible, including hit and present
    """
    new_possible = []
    for word in possible_words:
        match = True
        feedback = get_feedback(guess, word)
        for i in range(len(guess)):
            if feedback[i] == '0':
                if word[i] == guess[i]:
                    match = False
                    break
            elif feedback[i] == '?':
                if word[i] == guess[i] or guess[i] in word:
                    match = False
                    break
            elif feedback[i] == '_':
                # For '_', ensure the letter isn't in the word (considering multiple letters)
                if word[i] in guess:
                    match = False
                    break
        if match:
            new_possible.append(word)
    if not new_possible:
        return possible_words, False
    return new_possible, True

def score_word(guess, candidate):
    """
    Score the candidate by simulating feedback against all possible words.
    Counts how many times each feedback pattern occurs.
    """
    feedback = get_feedback(guess, candidate)
    # We want to pick the candidate that results in the fewest '0' and then '?'
    # So, count total '0' and '?' in the feedbacks
    total_g = feedback.count('0')
    total_y = feedback.count('?')
    return total_g, total_y

def choose_next_secret(guess, possible_words):
    """
    Select the next secret word with the fewest '0', then fewest '?' in the feedback
    when considering all possible guesses.
    """
    scored_candidates = []
    for candidate in possible_words:
        g_count, y_count = score_word(guess, candidate)
        scored_candidates.append((g_count, y_count, candidate))
    # Sort by fewest g, then fewest y
    scored_candidates.sort(key=lambda x: (x[0], x[1]))
    return scored_candidates[0][2]

def absurdle():
    possible_words = WORD_LIST.copy()
    # Initialize the secret word
    secret_word = "!!!!!"
    max_attempts = 10

    print("Welcome to Absurdle! Try to guess the word.")
    for attempt in range(1, max_attempts + 1):
        guess = input(f"Attempt {attempt}: ").lower()
        if len(guess) != 5:
            print("Please enter a 5-letter word.")
            continue
        if guess not in WORD_LIST:
            print("Word not in dictionary.")
            continue

        # Filter possible words based on guess
        possible_words, new = filter_word_list(possible_words, guess)

        if not possible_words:
            print("No possible words remaining. Something's wrong.")
            return

        # Choose next secret with minimal '0' and '?'
        # Select secret if word list can't be further filtered
        secret_word = choose_next_secret(guess, possible_words)
        if not new:
            possible_words = [secret_word]

        feedback = get_feedback(guess, secret_word)

        print("Feedback:", ''.join(feedback))

        if feedback == '00000':
            print("Congratulations! You guessed the word.")
            return

    print(f"Game over! The word was: {secret_word}")

if __name__ == "__main__":
    # List of 5-letter words (you can expand this list)
    WORD_LIST = [
        "apple", "brave", "crane", "dwarf", "eagle",
        "flame", "grape", "house", "index", "jolly",
        "knife", "lemon", "mango", "night", "ocean",
        "party", "queen", "roast", "stone", "trust",
        "urban", "vigor", "waltz", "xenon", "yacht", "zebra"
    ]

    # WORD_LIST = [
    #     "hello", "world", "quite", "fancy", "fresh", "panic", "crazy", "buggy", "scare",
    # ]
    absurdle()