import tkinter as tk
from tkinter import messagebox, ttk
import random
import copy

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Game")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')
        
        # Game state
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
        self.initial_board = [[0 for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        
        self.setup_ui()
        self.generate_new_puzzle()
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="SUDOKU", font=('Arial', 24, 'bold'), 
                              bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # Game frame
        game_frame = tk.Frame(self.root, bg='#f0f0f0')
        game_frame.pack(pady=10)
        
        # Create the grid
        self.cells = []
        self.canvas = tk.Canvas(game_frame, width=450, height=450, bg='white', highlightthickness=2)
        self.canvas.pack()
        
        # Create entry widgets for each cell
        for i in range(9):
            row = []
            for j in range(9):
                # Calculate position
                x = j * 50 + 25
                y = i * 50 + 25
                
                # Create entry widget
                entry = tk.Entry(self.canvas, width=2, font=('Arial', 16, 'bold'),
                               justify='center', bd=0, highlightthickness=1)
                entry.bind('<KeyPress>', lambda e, r=i, c=j: self.on_key_press(e, r, c))
                entry.bind('<Button-1>', lambda e, r=i, c=j: self.select_cell(r, c))
                entry.bind('<FocusIn>', lambda e, r=i, c=j: self.select_cell(r, c))
                
                # Place entry in canvas
                entry_window = self.canvas.create_window(x, y, window=entry)
                row.append(entry)
            self.cells.append(row)
        
        # Draw grid lines
        self.draw_grid()
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=20)
        
        # Buttons
        tk.Button(control_frame, text="New Game", command=self.generate_new_puzzle,
                 font=('Arial', 12), bg='#4CAF50', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(control_frame, text="Check Solution", command=self.check_solution,
                 font=('Arial', 12), bg='#2196F3', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(control_frame, text="Hint", command=self.give_hint,
                 font=('Arial', 12), bg='#FF9800', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(control_frame, text="Solve", command=self.show_solution,
                 font=('Arial', 12), bg='#f44336', fg='white', padx=20).pack(side=tk.LEFT, padx=10)
        
        # Difficulty selection
        difficulty_frame = tk.Frame(self.root, bg='#f0f0f0')
        difficulty_frame.pack(pady=10)
        
        tk.Label(difficulty_frame, text="Difficulty:", font=('Arial', 12), bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.difficulty_var = tk.StringVar(value="Medium")
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var,
                                       values=["Easy", "Medium", "Hard"], state="readonly", width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Welcome to Sudoku!", 
                                   font=('Arial', 12), bg='#f0f0f0', fg='#666')
        self.status_label.pack(pady=10)
    
    def draw_grid(self):
        # Draw thin lines
        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            # Vertical lines
            self.canvas.create_line(i * 50, 0, i * 50, 450, width=width, fill='black')
            # Horizontal lines
            self.canvas.create_line(0, i * 50, 450, i * 50, width=width, fill='black')
    
    def select_cell(self, row, col):
        # Reset previous selection
        if self.selected_cell:
            prev_row, prev_col = self.selected_cell
            self.cells[prev_row][prev_col].configure(highlightbackground='white')
        
        # Highlight new selection
        self.selected_cell = (row, col)
        self.cells[row][col].configure(highlightbackground='blue', highlightthickness=2)
        self.cells[row][col].focus_set()
    
    def on_key_press(self, event, row, col):
        key = event.char
        if key.isdigit() and key != '0':
            # Clear the cell first
            self.cells[row][col].delete(0, tk.END)
            # Insert the new digit
            self.cells[row][col].insert(0, key)
            self.board[row][col] = int(key)
            
            # Check if move is valid
            if not self.is_valid_move(row, col, int(key)):
                self.cells[row][col].configure(fg='red')
                self.status_label.configure(text="Invalid move! Number conflicts with row, column, or 3x3 box.", fg='red')
            else:
                self.cells[row][col].configure(fg='blue')
                self.status_label.configure(text="Good move!", fg='green')
            
            return "break"
        elif event.keysym in ['BackSpace', 'Delete']:
            self.cells[row][col].delete(0, tk.END)
            self.board[row][col] = 0
            self.cells[row][col].configure(fg='blue')
            self.status_label.configure(text="Cell cleared.", fg='black')
            return "break"
        else:
            return "break"  # Prevent other characters
    
    def is_valid_move(self, row, col, num):
        # Save current value
        temp = self.board[row][col]
        self.board[row][col] = 0  # Temporarily remove to check
        
        # Check row
        for c in range(9):
            if self.board[row][c] == num:
                self.board[row][col] = temp
                return False
        
        # Check column
        for r in range(9):
            if self.board[r][col] == num:
                self.board[row][col] = temp
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.board[r][c] == num:
                    self.board[row][col] = temp
                    return False
        
        self.board[row][col] = temp
        return True
    
    def generate_new_puzzle(self):
        # Clear the board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Generate a complete valid Sudoku
        self.solve_sudoku(self.board)
        self.solution = copy.deepcopy(self.board)
        
        # Remove numbers based on difficulty
        difficulty = self.difficulty_var.get()
        if difficulty == "Easy":
            cells_to_remove = 40
        elif difficulty == "Medium":
            cells_to_remove = 50
        else:  # Hard
            cells_to_remove = 60
        
        # Remove random cells
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i in range(cells_to_remove):
            row, col = cells[i]
            self.board[row][col] = 0
        
        self.initial_board = copy.deepcopy(self.board)
        self.update_display()
        self.status_label.configure(text=f"New {difficulty} puzzle generated!", fg='green')
    
    def solve_sudoku(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)  # Randomize for variety
                    
                    for num in numbers:
                        if self.is_valid_sudoku_move(board, i, j, num):
                            board[i][j] = num
                            if self.solve_sudoku(board):
                                return True
                            board[i][j] = 0
                    return False
        return True
    
    def is_valid_sudoku_move(self, board, row, col, num):
        # Check row
        for c in range(9):
            if board[row][c] == num:
                return False
        
        # Check column
        for r in range(9):
            if board[r][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if board[r][c] == num:
                    return False
        
        return True
    
    def update_display(self):
        for i in range(9):
            for j in range(9):
                self.cells[i][j].delete(0, tk.END)
                if self.board[i][j] != 0:
                    self.cells[i][j].insert(0, str(self.board[i][j]))
                    if self.initial_board[i][j] != 0:
                        # Initial numbers (black and non-editable)
                        self.cells[i][j].configure(fg='black', font=('Arial', 16, 'bold'))
                        self.cells[i][j].configure(state='readonly')
                    else:
                        # User numbers (blue and editable)
                        self.cells[i][j].configure(fg='blue', font=('Arial', 16))
                        self.cells[i][j].configure(state='normal')
                else:
                    self.cells[i][j].configure(fg='blue', font=('Arial', 16))
                    self.cells[i][j].configure(state='normal')
    
    def check_solution(self):
        # Check if board is complete
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    self.status_label.configure(text="Puzzle not complete yet!", fg='orange')
                    return
        
        # Check if solution is valid
        if self.is_valid_complete_board():
            messagebox.showinfo("Congratulations!", "Puzzle solved correctly! Well done!")
            self.status_label.configure(text="Puzzle solved! Congratulations!", fg='green')
        else:
            self.status_label.configure(text="Solution contains errors. Keep trying!", fg='red')
    
    def is_valid_complete_board(self):
        # Check all rows, columns, and 3x3 boxes
        for i in range(9):
            # Check row
            if len(set(self.board[i])) != 9 or 0 in self.board[i]:
                return False
            
            # Check column
            column = [self.board[j][i] for j in range(9)]
            if len(set(column)) != 9 or 0 in column:
                return False
        
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = []
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        box.append(self.board[r][c])
                if len(set(box)) != 9 or 0 in box:
                    return False
        
        return True
    
    def give_hint(self):
        # Find empty cells
        empty_cells = [(i, j) for i in range(9) for j in range(9) if self.board[i][j] == 0]
        
        if not empty_cells:
            self.status_label.configure(text="No empty cells to give hint for!", fg='orange')
            return
        
        # Pick random empty cell and fill with solution
        row, col = random.choice(empty_cells)
        correct_value = self.solution[row][col]
        
        self.board[row][col] = correct_value
        self.cells[row][col].delete(0, tk.END)
        self.cells[row][col].insert(0, str(correct_value))
        self.cells[row][col].configure(fg='green', font=('Arial', 16, 'bold'))
        
        self.status_label.configure(text=f"Hint: Cell ({row+1}, {col+1}) = {correct_value}", fg='green')
    
    def show_solution(self):
        result = messagebox.askyesno("Show Solution", "Are you sure you want to see the complete solution?")
        if result:
            self.board = copy.deepcopy(self.solution)
            self.update_display()
            self.status_label.configure(text="Solution revealed!", fg='blue')

def main():
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()