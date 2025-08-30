import socket
import threading
import tkinter as tk
from tkinter import ttk

# Colors for feedback
COLOR_DEFAULT = "#cccccc"
COLOR_CORRECT = "#6aaa64"    # Green
COLOR_PRESENT = "#c9b458"    # Yellow
COLOR_ABSENT = "#787c7e"     # Grey

class WordleClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Multiplayer Client")
        self.sock = None
        self.create_text_area()
        self.create_guess_frame()
        self.connect_to_server()
        self.feedback_keys = {}  # To track key colors
        self.setup_keyboard()

        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_server, daemon=True)
        self.listen_thread.start()

    def create_text_area(self):
        # Message display
        self.text_area = tk.Text(self.master, width=60, height=15, state='disabled')
        self.text_area.grid(row=0, column=0, columnspan=10, padx=10, pady=10)

    def create_guess_frame(self):
        # Frame for guess display
        self.guess_frame = tk.Frame(self.master)
        self.guess_frame.grid(row=1, column=0, columnspan=10)

        self.guess_labels = []
        for i in range(6):  # Max 6 guesses
            row_labels = []
            for j in range(5):
                lbl = tk.Label(self.guess_frame, text=' ', width=4, height=2, relief='solid', font=('Arial', 14))
                lbl.grid(row=i, column=j, padx=2, pady=2)
                row_labels.append(lbl)
            self.guess_labels.append(row_labels)

        # Virtual keyboard frame
        self.keyboard_frame = tk.Frame(self.master)
        self.keyboard_frame.grid(row=2, column=0, pady=10)

        # Entry for input
        self.input_entry = tk.Entry(self.master, width=10, font=('Arial', 14))
        self.input_entry.grid(row=3, column=0, pady=5)
        self.input_entry.bind('<Return>', lambda e: self.send_input())

    def setup_keyboard(self):
        # Define QWERTY layout
        keys = [
            "Q W E R T Y U I O P",
            "A S D F G H J K L",
            "Z X C V B N M"
        ]

        self.key_buttons = {}
        for r, row in enumerate(keys):
            row_frame = tk.Frame(self.keyboard_frame)
            row_frame.pack(pady=2)
            for ch in row.split():
                btn = tk.Button(row_frame, text=ch, width=4, height=2, bg=COLOR_DEFAULT,
                                command=lambda c=ch: self.key_press(c))
                btn.pack(side='left', padx=2)
                self.key_buttons[ch] = btn
                self.feedback_keys[ch] = COLOR_DEFAULT

        # Add Enter and Backspace keys
        control_frame = tk.Frame(self.master)
        control_frame.grid(row=4, column=0, pady=10)
        self.enter_btn = tk.Button(control_frame, text='Enter', width=6, command=self.send_input)
        self.enter_btn.pack(side='left', padx=5)
        self.backspace_btn = tk.Button(control_frame, text='Backspace', width=8, command=self.backspace)
        self.backspace_btn.pack(side='left', padx=5)

        # Keep track of current guess
        self.current_guess = ''
        self.current_row = 0

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 65432))
            self.append_message("Connected to server.")
        except Exception as e:
            self.append_message(f"Connection error: {e}")

    def listen_server(self):
        try:
            while True:
                data = self.sock.recv(1024).decode()
                if not data:
                    self.append_message("Disconnected from server.")
                    break
                self.handle_server_message(data)
        except Exception as e:
            # self.append_message(f"Error: {e}")
            self.append_message("Disconnected from server.")

    def handle_server_message(self, message):
        message = message.strip()
        self.append_message(message)

        # Handle new round
        if ("Next round starting" in message):
            self.create_guess_frame()
            self.setup_keyboard()

        # Detect prompts for input
        if ("Enter" in message) or ("Your turn" in message) or ("type 'start'" in message.lower()) or ("Invalid guess" in message) or ("Try again" in message):
            self.enable_input()
        else:
            self.disable_input()

        # End game: disable input
        if "Thanks for playing" in message or "Game over" in message:
            self.disable_input()

        # Process guesses and feedback
        if message.startswith("Guess:"):
            # Parse feedback line
            parts = message.split("Feedback:")
            if len(parts) == 2:
                guess_part = parts[0].replace("Guess:", "").strip()
                feedback_part = parts[1].strip()
                self.update_guess_row(self.current_row, guess_part, feedback_part)
                self.current_row += 1
                if "Game over" in message:
                    # Reset for new game
                    self.current_row = 0
        # Additional handling can be added here

    def update_guess_row(self, row_idx, guess, feedback):
        for i, ch in enumerate(guess.upper()):
            lbl = self.guess_labels[row_idx][i]
            lbl.config(text=ch)
            color = self.feedback_color(feedback[i])
            lbl.config(bg=color)
        # Update keyboard key colors
        for ch, fb in zip(guess.upper(), feedback):
            self.update_key_color(ch, fb)

    def feedback_color(self, feedback_char):
        if feedback_char == '0':
            return COLOR_CORRECT
        elif feedback_char == '?':
            return COLOR_PRESENT
        elif feedback_char == '_':
            return COLOR_ABSENT
        else:
            return COLOR_DEFAULT

    def update_key_color(self, ch, feedback_char):
        color = self.feedback_color(feedback_char)
        btn = self.key_buttons.get(ch)
        if btn:
            # Only upgrade color if better
            current_color = self.feedback_keys.get(ch, COLOR_DEFAULT)
            if self.color_better(color, current_color):
                btn.config(bg=color)
                self.feedback_keys[ch] = color

    def color_better(self, new_color, current_color):
        # Priority: GREEN > YELLOW > GRAY
        priority = {COLOR_CORRECT: 3, COLOR_PRESENT: 2, COLOR_ABSENT: 1, COLOR_DEFAULT: 0}
        return priority[new_color] > priority.get(current_color, 0)

    def send_input(self):
        # Send input from entry
        message = self.input_entry.get().strip()
        if message:
            self.sock.sendall(message.encode())
            self.input_entry.delete(0, tk.END)

    def key_press(self, ch):
        # Append letter to input_entry
        self.input_entry.insert("end", ch)

    def backspace(self):
        self.input_entry.delete(len(self.input_entry.get())-1)

    def disable_input(self):
        self.enter_btn.config(state='disabled')
        self.input_entry.config(state='disabled')
        for btn in self.key_buttons.values():
            btn.config(state='disabled')

    def enable_input(self):
        self.enter_btn.config(state='normal')
        self.input_entry.config(state='normal')
        for btn in self.key_buttons.values():
            btn.config(state='normal')

    def append_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = WordleClientGUI(root)
    root.mainloop()