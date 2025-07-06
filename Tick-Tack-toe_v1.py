"""
MIT License

Copyright (c) [2025] [thjedi64]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys, os, random, pickle, time
import tkinter as tk
from tkinter import messagebox, simpledialog

# =================== ADMIN PROMPT (Windows only) ===================
if sys.platform == "win32":
    import ctypes

    def is_running_as_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_running_as_admin():
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )
        sys.exit(0)

# =================== AI MEMORY ===================
AI_MEMORY_FILE = "ai_memory.pkl"

if os.path.exists(AI_MEMORY_FILE):
    with open(AI_MEMORY_FILE, "rb") as f:
        ai_memory = pickle.load(f)
else:
    ai_memory = {}

def save_ai_memory():
    with open(AI_MEMORY_FILE, "wb") as f:
        pickle.dump(ai_memory, f)

# =================== MAIN GAME CLASS ===================
class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe with Learning AI")
        self.mode = None
        self.current_player = "X"
        self.buttons = []
        self.board = [" " for _ in range(9)]
        self.last_state = None
        self.last_move = None
        self.setup_menu()

    def setup_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Tic-Tac-Toe", font=("Arial", 24)).pack(pady=20)
        tk.Button(self.root, text="Multiplayer", width=25, height=2,
                  command=lambda: self.start_game("multiplayer")).pack(pady=10)
        tk.Button(self.root, text="Vs AI", width=25, height=2,
                  command=lambda: self.start_game("vs_ai")).pack(pady=10)
        tk.Button(self.root, text="AI Learn (self-play)", width=25, height=2,
                  command=self.ai_learn_mode).pack(pady=10)
        tk.Button(self.root, text="Reset AI Memory", width=25, height=2,
                  command=self.reset_ai_memory).pack(pady=10)
        tk.Button(self.root, text="Quit", width=25, height=2,
                  command=lambda: (save_ai_memory(), self.root.quit())).pack(pady=10)

    def start_game(self, mode):
    	self.mode = mode
    	self.current_player = "X"
    	self.board = [" " for _ in range(9)]
    	self.last_state, self.last_move = None, None
    	for widget in self.root.winfo_children():
        	widget.destroy()
    	frame = tk.Frame(self.root)
    	frame.pack()
    	self.buttons = []
    	for i in range(9):
        	btn = tk.Button(frame, text=" ", width=10, height=4,
                        	command=lambda i=i: self.make_move(i))
        	btn.grid(row=i // 3, column=i % 3)
        	self.buttons.append(btn)
    	tk.Button(self.root, text="Back to Menu", command=self.setup_menu).pack(pady=10)
    	tk.Label(self.root, text="v1 - © thjedi64", font=("Arial", 10)).pack(pady=5)

    def make_move(self, idx):
        if self.board[idx] != " ":
            return
        self.board[idx] = self.current_player
        self.buttons[idx].config(text=self.current_player, state="disabled")
        if self.check_winner(self.current_player):
            messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
            self.disable_all_buttons()
            if self.mode == "vs_ai":
                self.learn_from_result("win" if self.current_player == "O" else "loss")
            return
        elif self.is_draw():
            messagebox.showinfo("Game Over", "It's a draw!")
            self.disable_all_buttons()
            self.learn_from_result("draw")
            return
        if self.mode == "multiplayer":
            self.current_player = "O" if self.current_player == "X" else "X"
        elif self.mode == "vs_ai":
            self.current_player = "O"
            self.root.after(200, self.ai_move)

    def ai_move(self):
        state = "".join(self.board)
        if state not in ai_memory:
            ai_memory[state] = list(range(9))
        possible_moves = [m for m in ai_memory[state] if self.board[m] == " "]
        move = random.choice(possible_moves) if possible_moves else random.choice([i for i, v in enumerate(self.board) if v == " "])
        self.board[move] = "O"
        self.buttons[move].config(text="O", state="disabled")
        if self.check_winner("O"):
            messagebox.showinfo("Game Over", "AI wins!")
            self.disable_all_buttons()
            self.learn_from_result("win")
            return
        elif self.is_draw():
            messagebox.showinfo("Game Over", "It's a draw!")
            self.disable_all_buttons()
            self.learn_from_result("draw")
            return
        self.last_state, self.last_move = state, move
        self.current_player = "X"

    def disable_all_buttons(self):
        for btn in self.buttons:
            btn.config(state="disabled")

    def is_draw(self):
        return all(s in ["X", "O"] for s in self.board)

    def check_winner(self, player):
        wins = [[0,1,2], [3,4,5], [6,7,8], [0,3,6],
                [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
        return any(all(self.board[i]==player for i in combo) for combo in wins)

    def learn_from_result(self, result):
        if self.mode != "vs_ai" or not self.last_state:
            return
        if result == "win":
            ai_memory[self.last_state] = [self.last_move]
        elif result == "loss" and self.last_move in ai_memory.get(self.last_state, []):
            ai_memory[self.last_state].remove(self.last_move)
        save_ai_memory()

    def ai_learn_mode(self):
        duration = simpledialog.askinteger(
            "AI Self-Play", "Train AI for how many seconds?", minvalue=1, initialvalue=10
        )
        if not duration:
            return

        start_time = time.time()
        games_played = 0

        while time.time() - start_time < duration:
            board = [" " for _ in range(9)]
            current = "X"
            last_state, last_move = None, None

            while True:
                state = "".join(board)
                if state not in ai_memory:
                    ai_memory[state] = list(range(9))
                possible = [m for m in ai_memory[state] if board[m]==" "]
                move = (
                    random.choice(possible)
                    if possible
                    else random.choice([i for i, s in enumerate(board) if s==" "])
                )
                board[move] = current

                if last_state and current=="O":
                    if self.check_winner_on_board(board, current):
                        if last_move in ai_memory[last_state]:
                            ai_memory[last_state].remove(last_move)

                if self.check_winner_on_board(board, current):
                    break
                if all(s in ["X","O"] for s in board):
                    break

                if current=="O":
                    last_state, last_move = state, move

                current = "O" if current=="X" else "X"

            games_played += 1

        save_ai_memory()
        messagebox.showinfo(
            "AI Learning",
            f"AI played {games_played} self-play games in {duration} seconds."
        )

    def check_winner_on_board(self, board, player):
        wins = [[0,1,2], [3,4,5], [6,7,8], [0,3,6],
                [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
        return any(all(board[i]==player for i in combo) for combo in wins)

    def reset_ai_memory(self):
        global ai_memory
        if messagebox.askyesno("Reset AI", "Are you sure you want to reset the AI memory?"):
            ai_memory = {}
            save_ai_memory()
            messagebox.showinfo("AI Reset", "AI memory has been cleared.")

# =================== RUN APP ===================
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
