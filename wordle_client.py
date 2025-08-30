import socket

def main():
    host = '127.0.0.1'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        # Receive welcome message
        data = s.recv(1024)
        print(data.decode())

        while True:
            guess = input("Enter your 5-letter guess: ").lower()

            # Send guess to server
            s.sendall(guess.encode())

            # Receive feedback
            feedback = s.recv(1024).decode().strip()

            # Check for validation messages
            if "Invalid guess" in feedback or "Try again" in feedback:
                print(feedback)
                continue

            # Print feedback
            print(feedback)

            # Receive end game check
            check = s.recv(1024).decode().strip()

            # Check for win or game over messages
            # Print end game message
            if "Congratulations" in check or "Game over" in check:
                print(check)
                break

if __name__ == "__main__":
    main()