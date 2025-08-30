import socket
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

def validate_guess(guess):
    return len(guess) == 5 and guess.isalpha()

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            secret_word = random.choice(word_list)
            attempts_left = max_attempts
            conn.sendall(f"Welcome to Wordle!\nGuess the 5-letter word. You have {attempts_left} attempts.\n".encode())
            # The server does not reveal the secret to the client.

            while attempts_left > 0:
                data = conn.recv(1024)
                if not data:
                    break
                guess = data.decode().strip().lower()

                # Validate input
                if not validate_guess(guess):
                    conn.sendall(b"Invalid guess. Enter a 5-letter word.\n")
                    continue

                # Optional: check if guess is in the word list
                if guess not in word_list:
                    conn.sendall(b"Word not in list. Try again.\n")
                    continue

                feedback = get_feedback(guess, secret_word)
                conn.sendall(feedback.encode() + b"\n")

                if guess == secret_word:
                    conn.sendall(b"Congratulations! You guessed the word.\n")
                    break
                else:
                    conn.sendall(b"\n")

                attempts_left -= 1

            else:
                # Out of attempts
                conn.sendall(f"Game over! The word was '{secret_word}'.\n".encode())

if __name__ == "__main__":
    start_server()