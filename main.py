"""
SS Prediction Tool - Main Frontend
Fixed layout using grid() — responsive on any screen size.
All algorithms run locally — no Selenium, no external servers needed.
"""

from tkinter import *
import tkinter.messagebox
from tkinter import messagebox, scrolledtext
import tkinter as tk
import os

# ─── Local module imports (all .py files in same folder) ───────────────────
from PDB          import fetch_pdb_sequence
from preprocessing import process_dssp_pipeline
from GOR_I        import GOR_I
from GOR_IV       import GOR_IV
from PHD          import PHD
from w_plot       import w, plot

# ═══════════════════════════════════════════════════════════════════════════
# ROOT WINDOW
# ═══════════════════════════════════════════════════════════════════════════
root = Tk()
root.title("SS Prediction Tool")
root.state('zoomed')       # Maximized on startup
root.minsize(900, 650)
root.configure(bg="#f0f0f0")

v = tk.IntVar()

# Two-column layout
root.columnconfigure(0, weight=3)   # left  ~60 %
root.columnconfigure(1, weight=2)   # right ~40 %
root.rowconfigure(1, weight=1)

# ═══════════════════════════════════════════════════════════════════════════
# TITLE  (spans both columns)
# ═══════════════════════════════════════════════════════════════════════════
tk.Label(
    root,
    text="Secondary Structure Accuracy Prediction Tool",
    font=("Cambria", 18, "bold"),
    bg="#f0f0f0"
).grid(row=0, column=0, columnspan=2, pady=(10, 4), sticky="w", padx=12)

# ═══════════════════════════════════════════════════════════════════════════
# LEFT PANEL
# ═══════════════════════════════════════════════════════════════════════════
left_frame = tk.Frame(root, bg="#f0f0f0")
left_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))

left_frame.columnconfigure(1, weight=1)
left_frame.rowconfigure(2, weight=1)
left_frame.rowconfigure(6, weight=1)
left_frame.rowconfigure(8, weight=1)

# PDB ID
tk.Label(left_frame, text="Enter PDB ID:", font=("Arial", 9), bg="#f0f0f0").grid(
    row=0, column=0, sticky="w", pady=(6, 2))
e1 = tk.Entry(left_frame, width=20)
e1.grid(row=0, column=1, sticky="w", pady=(6, 2))

# Input box
tk.Label(left_frame, text="Enter Data Below:", font=("Arial", 9), bg="#f0f0f0").grid(
    row=1, column=0, sticky="w", pady=(4, 0))
input_box = scrolledtext.ScrolledText(left_frame, width=70, height=10)
input_box.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(2, 6))

# Method chooser + Process button
method_frame = tk.Frame(left_frame, bg="#f0f0f0")
method_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=4)

tk.Label(method_frame, text="Choose Method:", font=("Arial", 9), bg="#f0f0f0").pack(side="left")
tk.Radiobutton(method_frame, text="GOR I",  variable=v, value=1, bg="#f0f0f0").pack(side="left", padx=6)
tk.Radiobutton(method_frame, text="GOR IV", variable=v, value=2, bg="#f0f0f0").pack(side="left", padx=6)
tk.Radiobutton(method_frame, text="PHD",    variable=v, value=3, bg="#f0f0f0").pack(side="left", padx=6)

tk.Button(
    method_frame, text="Process",
    command=lambda: combined_function(),
    bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
    relief="raised", padx=10
).pack(side="left", padx=20)

# Formatted output
tk.Label(left_frame, text="Formatted Output:", font=("Arial", 9), bg="#f0f0f0").grid(
    row=5, column=0, sticky="w", pady=(4, 0))
output_box = scrolledtext.ScrolledText(left_frame, width=70, height=10)
output_box.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(2, 6))

# PDB sequence output
tk.Label(left_frame, text="PDB Sequence Output:", font=("Arial", 9), bg="#f0f0f0").grid(
    row=7, column=0, sticky="w", pady=(4, 0))
output_box_1 = scrolledtext.ScrolledText(left_frame, width=70, height=6)
output_box_1.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=(2, 6))

# ═══════════════════════════════════════════════════════════════════════════
# RIGHT PANEL  — Result + Graph (the red-box section, now properly placed)
# ═══════════════════════════════════════════════════════════════════════════
right_frame = tk.Frame(root, bg="#ffffff", relief="solid", bd=2)
right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))

right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(1, weight=1)
right_frame.rowconfigure(3, weight=2)

tk.Label(right_frame, text="RESULT", font=("Cambria", 14, "bold"), bg="#ffffff").grid(
    row=0, column=0, pady=(10, 4))
text_widget1 = tk.Text(right_frame, height=10, width=50, wrap="word")
text_widget1.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

tk.Label(right_frame, text="GRAPH", font=("Cambria", 14, "bold"), bg="#ffffff").grid(
    row=2, column=0, pady=(4, 4))
frame_graph = tk.Frame(right_frame, bg="#ffffff")
frame_graph.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))

# ═══════════════════════════════════════════════════════════════════════════
# MENU
# ═══════════════════════════════════════════════════════════════════════════
def onClick_about():
    about_file_path = "About the Creators.txt"
    if os.path.exists(about_file_path):
        about_window = Toplevel(root)
        about_window.title("About")
        about_window.geometry("400x300")
        about_text = scrolledtext.ScrolledText(about_window, wrap=tk.WORD, width=50, height=15)
        about_text.pack(padx=10, pady=10)
        with open(about_file_path, 'r') as file:
            about_content = file.read()
        about_text.insert(tk.INSERT, about_content)
        about_text.config(state=tk.DISABLED)
    else:
        tkinter.messagebox.showerror("Error", "About file not found.")


def saveFile():
    file_path = 'data.txt'
    with open(file_path, 'w') as f:
        f.write("Your data here")
    tkinter.messagebox.showinfo("Save", f"Data saved to {file_path}")


def openFile():
    file_path = 'data.txt'
    try:
        with open(file_path, 'r') as f:
            data = f.read()
        tkinter.messagebox.showinfo("Open", f"Data loaded: {data}")
    except FileNotFoundError:
        tkinter.messagebox.showerror("Error", "data.txt not found.")


menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New')
filemenu.add_command(label='Open...', command=openFile)
filemenu.add_command(label='Save', command=saveFile)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=root.quit)

helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About', command=onClick_about)

# ═══════════════════════════════════════════════════════════════════════════
# LOGIC FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════
def process_pdb():
    pdb_id = e1.get().strip()
    print(f"DEBUG: PDB ID = {pdb_id}")
    if pdb_id:
        result = fetch_pdb_sequence(pdb_id)
        print(f"DEBUG: process_pdb() result = {result}")
        output_box_1.delete("1.0", tk.END)
        output_box_1.insert(tk.END, result)
        return result
    else:
        messagebox.showwarning("Warning", "Please enter a PDB ID.")
        return None


def handle_processing():
    input_data = input_box.get("1.0", tk.END).strip()
    print(f"DEBUG: handle_processing() input_data = {input_data}")
    if not input_data:
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, "⚠️ Please provide input data.")
        return None
    processed_data = process_dssp_pipeline(input_data)
    print(f"DEBUG: handle_processing() processed_data = {processed_data}")
    return processed_data


def run_selected_method():
    stored_result  = process_pdb()
    process_result = handle_processing()
    print(f"DEBUG: stored_result = {stored_result}")
    print(f"DEBUG: process_result = {process_result}")

    if stored_result is None or process_result is None:
        return "⚠️ Error: Missing input data!"

    if v.get() == 1:
        return GOR_I(stored_result, process_result)  or "⚠️ GOR_I returned None!"
    elif v.get() == 2:
        return GOR_IV(stored_result, process_result) or "⚠️ GOR_IV returned None!"
    elif v.get() == 3:
        return PHD(stored_result, process_result)    or "⚠️ PHD returned None!"
    else:
        return "⚠️ No method selected! Please choose GOR I, GOR IV, or PHD."


final_result = None
w_result     = None
graph_drawn  = False


def final_def():
    try:
        result = run_selected_method()
        if result is None:
            result = "⚠️ No output generated!"

        if isinstance(result, dict) and "aligned_output" in result:
            Aligned_output = result["aligned_output"]
        else:
            Aligned_output = str(result)

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, Aligned_output)
        return result
    except Exception as e:
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, f"⚠️ Error occurred: {e}")
        return None


def result_graph():
    global final_result, w_result, graph_drawn

    if graph_drawn:
        return

    if final_result is None:
        final_result = final_def()

    if final_result and isinstance(final_result, dict):
        Aligned_output = final_result.get("aligned_output", "⚠️ Incomplete Data")
        mid_lines      = final_result.get("mid_lines",      [])
        next_lines     = final_result.get("next_lines",     [])
        sequence       = final_result.get("sequence",       "")

        w_result = w(Aligned_output, mid_lines, next_lines, sequence)

        if w_result is None:
            text_widget1.delete("1.0", tk.END)
            text_widget1.insert(tk.END, "⚠️ Error: Could not compute accuracy (length mismatch?).")
            text_widget1.config(state=tk.DISABLED)
            return

        report      = w_result["result_output"]
        X           = w_result["X"]
        Y           = w_result["Y"]
        Z           = w_result["Z"]
        Q3_accuracy = w_result["Q3_accuracy"]

        if not graph_drawn:
            plot(X, Y, Z, Q3_accuracy, frame_graph)
            graph_drawn = True

        text_widget1.delete("1.0", tk.END)
        text_widget1.insert(tk.END, report)
        text_widget1.config(state=tk.DISABLED)
    else:
        text_widget1.delete("1.0", tk.END)
        text_widget1.insert(tk.END, "⚠️ Error: No valid output generated!")
        text_widget1.config(state=tk.DISABLED)


def combined_function():
    global final_result, graph_drawn
    final_result = None   # reset so fresh run always works
    graph_drawn  = False
    process_pdb()
    handle_processing()
    result_graph()


# ═══════════════════════════════════════════════════════════════════════════
root.mainloop()
