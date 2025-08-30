import socket

def main():
    HOST = '127.0.0.1'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            print(data.strip())

            # Break on game over / room closed
            if "Thanks for playing" in data or "Game over" in data:
                break

            # Prompt for input if needed
            if ("Enter" in data) or ("Your turn" in data) or ("type 'start'" in data.lower()) or ("Invalid guess" in data) or ("Try again" in data):
                user_input = None
                while not user_input:
                  user_input = input()
                s.sendall(user_input.encode())

if __name__ == "__main__":
    main()