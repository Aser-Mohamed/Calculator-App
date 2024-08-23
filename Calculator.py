import tkinter as tk
from tkinter import ttk

# Function to update the input field whenever a button is pressed
def press(key):
    current = str(entry.get())
    entry.delete(0, tk.END)
    entry.insert(0, current + key)

# Function to evaluate the final expression
def equal():
    try:
        result = str(eval(entry.get()))
        entry.delete(0, tk.END)
        entry.insert(0, result)
    except:
        entry.delete(0, tk.END)
        entry.insert(0, "Error")

# Function to clear the input field
def clear():
    entry.delete(0, tk.END)

# Creating the main window
root = tk.Tk()
root.title("Modern UI Calculator")

# Styling the buttons and entry widget
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 15), padding=10)
style.configure('TEntry', font=('Helvetica', 20), padding=10)

# Creating the entry widget
entry = ttk.Entry(root, justify='right', width=15)
entry.grid(row=0, column=0, columnspan=4, sticky='nsew')

# Creating the calculator buttons
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
    ('0', 4, 1), ('+', 1, 3), ('-', 2, 3),
    ('*', 3, 3), ('/', 4, 3), ('=', 4, 2),
    ('C', 4, 0)
]

for (text, row, col) in buttons:
    if text == '=':
        btn = ttk.Button(root, text=text, command=equal)
    elif text == 'C':
        btn = ttk.Button(root, text=text, command=clear)
    else:
        btn = ttk.Button(root, text=text, command=lambda key=text: press(key))
    btn.grid(row=row, column=col, sticky='nsew')

# Making the grid expandable
for i in range(5):
    root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(i, weight=1)

# Running the application
root.mainloop()
