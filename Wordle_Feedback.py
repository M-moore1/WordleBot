import tkinter as tk
import os
from functools import partial

BOX_SIZE = 60
ROWS = 6
COLS = 5

# Load word list
path = os.getcwd() + '/Wordle/'
with open(path + 'wordlist.txt', 'r') as f:
    ALL_WORDS = [line.strip().upper() for line in f if len(line.strip()) == 5]

class WordleAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Assistant Bot")
        self.canvas = tk.Canvas(root, width=COLS * BOX_SIZE, height=ROWS * BOX_SIZE)
        self.canvas.pack()

        self.letters = [['' for _ in range(COLS)] for _ in range(ROWS)]
        self.colors = [['gray' for _ in range(COLS)] for _ in range(ROWS)]
        self.cells = {}
        self.current_row = 0
        self.current_col = 0
        self.possible_words = list(ALL_WORDS)

        self.suggestion_label = tk.Label(root, text="Suggested word: ", font=("Helvetica", 16))
        self.suggestion_label.pack(pady=10)

        self.draw_grid()
        self.root.bind("<Key>", self.on_key)

    def draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                x0, y0 = c * BOX_SIZE, r * BOX_SIZE
                x1, y1 = x0 + BOX_SIZE, y0 + BOX_SIZE
                rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="lightgray")
                text = self.canvas.create_text((x0 + x1)//2, (y0 + y1)//2, text='', font=("Helvetica", 24))
                self.cells[(r, c)] = (rect, text)
                self.canvas.tag_bind(rect, '<Button-1>', partial(self.on_click, row=r, col=c))

    def on_key(self, event):
        if self.current_row >= ROWS:
            return
        if event.keysym == "Return":
            if self.current_col == COLS:
                self.filter_words()
                self.show_suggestion()
                self.current_row += 1
                self.current_col = 0
        elif event.keysym == "BackSpace":
            if self.current_col > 0:
                self.current_col -= 1
                self.letters[self.current_row][self.current_col] = ''
                self.update_cell(self.current_row, self.current_col)
        elif event.char.isalpha() and self.current_col < COLS:
            letter = event.char.upper()
            self.letters[self.current_row][self.current_col] = letter
            self.update_cell(self.current_row, self.current_col)
            self.current_col += 1

    def cycle_color(self, row, col):
        current = self.colors[row][col]
        next_color = {'gray': 'yellow', 'yellow': 'green', 'green': 'gray'}[current]
        self.colors[row][col] = next_color
        self.update_cell(row, col)
        if row < self.current_row:
            self.filter_words()
            self.show_suggestion()

    def update_cell(self, row, col):
        letter = self.letters[row][col]
        color = self.colors[row][col]
        rect, text = self.cells[(row, col)]
        fill = {'gray': 'lightgray', 'yellow': 'gold', 'green': 'limegreen'}[color]
        self.canvas.itemconfig(rect, fill=fill)
        self.canvas.itemconfig(text, text=letter)

    def filter_words(self):
        filtered = list(ALL_WORDS)
        for row in range(self.current_row + 1):
            guess = self.letters[row]
            feedback = self.colors[row]
            filtered = self.apply_feedback(filtered, guess, feedback)
        self.possible_words = filtered

    def apply_feedback(self, words, guess, feedback):
        result = []
        for word in words:
            match = True
            word_list = list(word)
            temp_used = [False] * 5

            # Green check
            for i in range(5):
                if feedback[i] == 'green':
                    if word[i] != guess[i]:
                        match = False
                        break
                    temp_used[i] = True
            if not match:
                continue

            # Yellow / Gray check
            for i in range(5):
                if feedback[i] == 'yellow':
                    if guess[i] not in word or word[i] == guess[i]:
                        match = False
                        break
                elif feedback[i] == 'gray':
                    allowed = sum(1 for j in range(5) if guess[j] == guess[i] and feedback[j] in ['green', 'yellow'])
                    if word.count(guess[i]) > allowed:
                        match = False
                        break
            if match:
                result.append(word)
        return result

    def show_suggestion(self):
        if self.possible_words:
            suggestion = self.possible_words[0]
            self.suggestion_label.config(text=f"Suggested word: {suggestion}")
        else:
            self.suggestion_label.config(text="❌ No words remaining.")

    def on_click(self, event, row, col):
        self.cycle_color(row, col)

if __name__ == "__main__":
    root = tk.Tk()
    app = WordleAssistant(root)
    root.mainloop()