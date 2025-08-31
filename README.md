# Wordle-game

Welcome to the **Wordle-game** repository! This project is designed to demonstrate the programming practice in various aspects. A multi-player wordle is implemented as a solution.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Trade-off](#trade-off)
- [References](#references)

---

## Features

- Feature 1: Normal wordle $~~~~~~~~~~~~~$ [Selects a 5-letter word from predefined list, then player has 6 attempts to guess the word]
- Feature 2: Server/client wordle $~~~~~~$ [Supports the server / client model]
- Feature 3: Host cheating wordle $~~~~$ [Implements the concept of absurdle, where the game keeps a list of candidates instead of selecting the answer at the beginning]
- Feature 4: Multi-player wordle $~~~~~~~$ [Allows players to create or join room to play wordle together, they can cooperate to guess the words and defeat enemies to gain points. This game play allows more players to participate and build on others' efforts to win]
- Extra Feature: $~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~$ [GUI is implemented to improve user experience. Virtual keyboard with colored keys is included to help player remember the characters that are used]
---

## Installation

### Prerequisites

- Conda enviroment required
- See https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html for details

### Steps

1. Clone the repository:

```bash
git clone https://github.com/KCheng03/Wordle-game.git
```

2. Navigate into the project directory:

```bash
cd Wordle-game
```

3. Create conda environment:

```bash
conda env create -f environment.yml
```

---

## Usage

Explain how to start the game:

```bash
# Activate conda environment
conda activate pywordle

# Start the server
python wordle_server.py

# Start the client
python wordle_client.py
```

**Note:** Predefined word list can be changed at wordle_server.py (global variable: word_list)

---

## Trade-off

Though this project implements a GUI for the wordle game, the majority of the contents are text based. This helps reduce the complexity of the program and shorten development time, while limiting the user experience at the same time. On the other hand, the maintainability of the codes is kept. Only parts of the components or widgets need to be changed to provide a more comprehensive GUI.

---

## References

This project is based on the wordle games on the following websites.

1. Wordle - The New York Time [https://www.nytimes.com/games/wordle/index.html]
2. Absurdle - Absurdle Game [https://absurdle.online/]

---

*Feel free to use my project!*

