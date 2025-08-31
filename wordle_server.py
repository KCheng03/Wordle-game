import socket
import threading
import random
import time
from select import select
import wordle_cheat_host as wch

# Max attempts before round over
max_attempts = 6

# Max rounds before room close
max_rounds = 2


# List of 5-letter words (you can expand this list)
word_list = [
    "apple", "brave", "crane", "dwarf", "eagle",
    "flame", "grape", "house", "index", "jolly",
    "knife", "lemon", "mango", "night", "ocean",
    "party", "queen", "roast", "stone", "trust",
    "urban", "vigor", "waltz", "xenon", "yacht", "zebra"
]

# word_list = [
#     "hello", "world", "quite", "fancy", "fresh", "panic", "crazy", "buggy", "scare",
# ]

enemy = "*       %*-------==#%       \n    %-:  .:--------=+=#    \n   +-..:------------==++   \n  *-..---------------===*  \n  -:.:----------------=+-  \n %-------*%------**---===* \n +-..----%%------%*---==+- \n@=--------------------=++-@\n#==------------------==+=-+\n*=====------------====*+=-+\n@+=+++=============+++=-:=@\n  @@@@@@@@@@@@@@@@@@@@@@@"

HOST = '127.0.0.1'
PORT = 65432

# Data structure to manage rooms
rooms = {}  # {room_code: {'clients': [], 'game_in_progress': bool, 'secret_word': str, 'current_turn': int, 
            # 'current_health': int, 'rounds_played': int, 'max_rounds': int, 'total_score': int, 'possible_words': List}}

# Data structure to manage data
data = {}  # {conn: str}

lock = threading.Lock()

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

def handle_client(conn, addr):
    try:
        conn.sendall(b"Welcome! Enter room code to join or create: ")
        room_code = conn.recv(1024).decode().strip()

        with lock:
            if room_code not in rooms:
                # Create new room
                rooms[room_code] = {
                    'clients': [],
                    'game_in_progress': False,
                    'secret_word': None,
                    'current_turn': 0,
                    'current_health': max_attempts,
                    'rounds_played': 0,
                    'max_rounds': max_rounds,
                    'total_score': 0,
                    'possible_words': None,
                }
            if rooms.get(room_code)['game_in_progress']:
                conn.sendall(f"Game in progress. Not accepting new client.\n".encode())
                return
            rooms[room_code]['clients'].append(conn)
            conn.sendall(f"Joined room {room_code}. Waiting for start command.\n".encode())

        while True:
            with lock:
                room = rooms.get(room_code)
                if room is None:
                    break  # Room closed

                # Start game if not in progress and someone types 'start'
                if not room['game_in_progress']:
                    conn.sendall(f"{len(room['clients'])} clients in the room.\n".encode())
                    if conn == room['clients'][0]:
                        conn.sendall(b"Type 'start' to begin the game. Type 'r' to refresh.\n")
            
            # Receive input
            data[conn] = conn.recv(1024)
            if not data[conn]:
                conn.sendall(b"Data lost. Try again.\n")
                continue
            message = data[conn].decode().strip()
            print(conn, message, flush=True)

            with lock:
                room = rooms.get(room_code)
                if room is None:
                    conn.sendall(b"Room closed unexpectedly.\n")
                    break

                # Handle start command
                if not room['game_in_progress'] and message.lower() == 'start':
                    # Initialize game
                    room['secret_word'] = "!!!!!"
                    room['game_in_progress'] = True
                    room['current_turn'] = 0
                    room['current_health'] = max_attempts
                    room['rounds_played'] += 1
                    room["possible_words"] = word_list.copy()
                    # Notify all clients
                    for c in room['clients']:
                        c.sendall(b"Game starting!\n")
                        time.sleep(0.2)
                        c.sendall(f"Enemy appears!\n".encode())
                        time.sleep(1)
                        c.sendall(f"\n{enemy}\n*\n".encode())
                        time.sleep(0.2)
                        c.sendall(f"Guess the 5-letter word to attack. You have {room['current_health']} attempts.\n".encode())
                        
                        # Prompt first player to start
                        if c != room['clients'][room['current_turn']]:
                            c.sendall(b"Waiting for your turn...\n")
                        else:
                            c.sendall(b"Your turn! Enter your guess:\n")
                    continue
                elif not room['game_in_progress']:
                    # Waiting for start
                    continue

                # Game in progress
                current_client = room['clients'][room['current_turn']]
                if conn != current_client:
                    # Not this client's turn
                    conn.sendall(b"Waiting for your turn...\n")
                    continue
                else:
                    # It's this client's turn
                    # Validate guess
                    guess = message.lower()
                    if len(guess) != 5 or not guess.isalpha():
                        conn.sendall(b"Invalid guess. Enter a 5-letter word.\n")
                        continue
                    if guess not in word_list:
                        conn.sendall(b"Word not in list. Try again.\n")
                        continue

                    # Filter possible words based on guess
                    room['possible_words'], new = wch.filter_word_list(room['possible_words'], guess)

                    # Choose next secret with minimal '0' and '?'
                    # Select secret if word list can't be further filtered
                    room['secret_word'] = wch.choose_next_secret(guess, room['possible_words'])
                    if not new:
                        room['possible_words'] = [room['secret_word']]
                    
                    feedback = get_feedback(guess, room['secret_word'])
                    # Send feedback to all clients
                    for c in room['clients']:
                        c.sendall(f"Guess: {guess}    Feedback: {feedback}\n".encode())

                    if guess == room['secret_word']:
                        # Win
                        room['total_score'] += 1
                        for c in room['clients']:
                            c.sendall(b"Congratulations! You guessed the word.\n")
                            time.sleep(1)
                            c.sendall(b"Enemy defeated. You gained one point!\n")
                            time.sleep(2)
                    else:
                        # Game over check
                        room['current_health'] -= 1
                        if room['current_health'] < 1:
                            for c in room['clients']:
                                # Out of attempts
                                c.sendall(f"Enemy escaped! The word was '{room['secret_word']}'.\n".encode())
                                time.sleep(2)
                        else:
                            # Next turn
                            room['current_turn'] = (room['current_turn'] + 1) % len(room['clients'])
                            # Prompt next player
                            room['clients'][room['current_turn']].sendall(b"Your turn! Enter your guess:\n")
                            continue
                    
                    # Prepare for next round or close
                    # room['game_in_progress'] = False       
                    if room['rounds_played'] >= room['max_rounds']:
                        for c in room['clients']:
                            c.sendall(f"Your total score is {room['total_score']}!\n".encode())
                            c.sendall(b"Room closed. Thanks for playing!\n")
                        time.sleep(5)
                        for c in room['clients']:
                            c.close()
                        del rooms[room_code]
                    else:
                        # Start new game
                        room['secret_word'] = "!!!!!"
                        room['current_turn'] = 0
                        room['current_health'] = max_attempts
                        room['rounds_played'] += 1
                        room["possible_words"] = word_list.copy()
                        for c in room['clients']:
                            c.sendall(b"Next round starting!\n")
                            time.sleep(0.2)
                            c.sendall(f"Enemy appears!\n".encode())
                            time.sleep(1)
                            c.sendall(f"\n{enemy}\n*\n".encode())
                            time.sleep(0.2)
                            c.sendall(f"Guess the 5-letter word to attack. You have {room['current_health']} attempts.\n".encode())
                            # Prompt first player to start
                            if c != room['clients'][room['current_turn']]:
                                c.sendall(b"Waiting for your turn...\n")
                            else:
                                c.sendall(b"Your turn! Enter your guess:\n")
    except Exception as e:
        print(f"Error handling client {addr}: {e}", flush=True)
    finally:
        # Remove client
        with lock:
            for room_code, room in list(rooms.items()):
                if conn in room['clients']:
                    room['clients'].remove(conn)
                    if not room['clients']:
                        del rooms[room_code]
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            ready, _, _ = select([s], [], [], 1) #Timeout set to 1 seconds
            if ready:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            else:
                pass
            

if __name__ == "__main__":
    main()