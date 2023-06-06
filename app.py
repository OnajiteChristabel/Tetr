import tkinter as tk
import random
from threading import Lock
from pygame import mixer
from PIL import Image, ImageTk

def play_song():
    mixer.init()
    mixer.music.load("song.mp3")
    mixer.music.play()

def stop_song():
    mixer.music.stop()

COLORS = ['gray', 'white', 'red', 'blue', 'orange', 'purple']

class Tetris():
    FIELD_HEIGHT = 20
    FIELD_WIDTH = 10
    SCORE_PER_ELIMINATED_LINES = (0, 40, 100, 300, 1200)
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1,1)], # O
        [(0, 0), (0, 1), (1, 1), (2,1)], # L
        [(0, 1), (1, 1), (2, 1), (2,0)], # J 
        [(0, 1), (1, 0), (1, 1), (2,0)], # Z
        [(0, 1), (1, 0), (1, 1), (2,1)], # T
        [(0, 0), (1, 0), (1, 1), (2,1)], # S
        [(0, 1), (1, 1), (2, 1), (3,1)], # I
    ]
    
    def __init__(self):
        self.field = [[0 for c in range(Tetris.FIELD_WIDTH)] for r in range(Tetris.FIELD_HEIGHT)]
        self.score = 0
        self.level = 0
        self.total_lines_eliminated = 0
        self.game_over = False
        self.move_lock = Lock()
        self.reset_tetromino()

    def reset_tetromino(self):
        self.tetromino = random.choice(Tetris.TETROMINOS)[:]
        self.tetromino_color = random.randint(1, len(COLORS)-1)
        self.tetromino_offset = [-2, Tetris.FIELD_WIDTH//2]
        self.game_over = any(not self.is_cell_free(r, c) for (r, c) in self.get_tetromino_coords())
    
    def get_tetromino_coords(self):
        return [(r+self.tetromino_offset[0], c + self.tetromino_offset[1]) for (r, c) in self.tetromino]

    def apply_tetromino(self):
        for (r, c) in self.get_tetromino_coords():
            self.field[r][c] = self.tetromino_color

        new_field = [row for row in self.field if any(tile == 0 for tile in row)]
        lines_eliminated = len(self.field)-len(new_field)
        self.total_lines_eliminated += lines_eliminated
        self.field = [[0]*Tetris.FIELD_WIDTH for x in range(lines_eliminated)] + new_field
        self.score += Tetris.SCORE_PER_ELIMINATED_LINES[lines_eliminated] * (self.level + 1)
        self.level = self.total_lines_eliminated // 10
        self.reset_tetromino()

    def get_color(self, r, c):
        return self.tetromino_color if (r, c) in self.get_tetromino_coords() else self.field[r][c]
    
    def is_cell_free(self, r, c):
        return r >= 0 and c >= 0 and r < Tetris.FIELD_HEIGHT and c < Tetris.FIELD_WIDTH and self.field[r][c] == 0

    def move_tetromino(self, dr, dc):
        with self.move_lock:
            for (r, c) in self.get_tetromino_coords():
                if not self.is_cell_free(r+dr, c+dc):
                    return False
            self.tetromino_offset[0] += dr
            self.tetromino_offset[1] += dc
            return True

    def rotate_tetromino(self):
        with self.move_lock:
            original_tetromino = self.tetromino
            self.tetromino = [(c, -r) for (r, c) in self.tetromino[::-1]]
            if not all(self.is_cell_free(r+self.tetromino_offset[0], c+self.tetromino_offset[1]) for (r, c) in self.get_tetromino_coords()):
                self.tetromino = original_tetromino

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('500x600')
        self.master.bind('<KeyPress>', self.on_key_press)
        self.master.bind('<KeyRelease>', self.on_key_release)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=400, height=400, bg='black')
        self.canvas.pack(side="top")

        self.score_label = tk.Label(self, text="Score: 0", font=("Helvetica", 16))
        self.score_label.pack(side="top")

        self.level_label = tk.Label(self, text="Level: 0", font=("Helvetica", 16))
        self.level_label.pack(side="top")

    def on_key_press(self, event):
        if event.keysym == 'Up':
            game.rotate_tetromino()
        elif event.keysym == 'Down':
            self.after(50, self.move_tetromino_down)
        elif event.keysym == 'Left':
            self.move_tetromino_sideways(-1)
        elif event.keysym == 'Right':
            self.move_tetromino_sideways(1)

    def on_key_release(self, event):
        if event.keysym == 'Down':
            self.after_cancel(self.after_id)

    def move_tetromino_down(self):
        if game.move_tetromino(1, 0):
            self.redraw()
            self.after_id = self.after(500 - 50*game.level, self.move_tetromino_down)
        else:
            game.apply_tetromino()
            if game.game_over:
                self.game_over()

    def move_tetromino_sideways(self, direction):
        game.move_tetromino(0, direction)
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        for r in range(Tetris.FIELD_HEIGHT):
            for c in range(Tetris.FIELD_WIDTH):
                color = COLORS[game.get_color(r, c)]
                x1, y1 = c * 20, r * 20
                x2, y2 = x1 + 20, y1 + 20
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        
        self.score_label["text"] = f"Score: {game.score}"
        self.level_label["text"] = f"Level: {game.level}"

    def game_over(self):
        self.canvas.delete("all")
        x1, y1 = 50, 200
        x2, y2 = x1 + 300, y1 + 100
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='white')
        self.canvas.create_text(200, 250, text="Game Over", font=("Helvetica", 30))

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
