# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import seaborn as sns


# def w(Aligned_output, mid_lines, next_lines, sequence):
#     predicted_structure = mid_lines[2]
#     absolute_structure  = next_lines[1].lower()

#     if len(predicted_structure) != len(absolute_structure):
#         print("Error: Predicted and absolute structures must be of the same length!")
#         return None

#     match_c = match_h = match_e = 0

#     for pred, abs_char in zip(predicted_structure, absolute_structure):
#         if pred == abs_char:
#             if pred == 'c':
#                 match_c += 1
#             elif pred == 'h':
#                 match_h += 1
#             elif pred == 'e':
#                 match_e += 1

#     X = match_h
#     Y = match_e
#     Z = match_c
#     Total_len = len(sequence)
#     Q3_accuracy = ((X + Y + Z) / Total_len) * 100 if Total_len > 0 else 0.0

#     result_output = (
#         f"No. of AAR correctly predicted in sec structure H: {X}\n"
#         f"No. of AAR correctly predicted in sec structure E: {Y}\n"
#         f"No. of AAR correctly predicted in sec structure C: {Z}\n"
#         f"Total length of the sequence: {Total_len}\n"
#         f"Q3 Accuracy: {Q3_accuracy:.2f}%"
#     )

#     return {
#         "X":             X,
#         "Y":             Y,
#         "Z":             Z,
#         "Q3_accuracy":   Q3_accuracy,
#         "result_output": result_output,
#     }


# def plot(X, Y, Z, Q3_accuracy, frame):
#     categories = ['Helix (H)', 'Strand (E)', 'Coil (C)']
#     values     = [X, Y, Z]

#     fig = Figure(figsize=(6, 4), dpi=100)
#     ax  = fig.add_subplot(111)

#     sns.barplot(x=categories, y=values, palette=['blue', 'red', 'green'], ax=ax)
#     ax.axhline(
#         y=Q3_accuracy, color='black', linestyle='--',
#         label=f'Q3 Accuracy: {Q3_accuracy:.2f}%'
#     )

#     ax.set_xlabel('Secondary Structure Type')
#     ax.set_ylabel('Correctly Predicted Residues')
#     ax.set_title('Correctly Predicted Secondary Structures & Q3 Accuracy')
#     ax.legend()

#     canvas = FigureCanvasTkAgg(fig, master=frame)
#     canvas.draw()
#     canvas.get_tk_widget().pack(fill='both', expand=True)



from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import tkinter as tk

# ── Graph history store ────────────────────────────────────────────────────
_graphs = []        # list of (X, Y, Z, Q3_accuracy, label) tuples
_current_idx = [0]  # mutable so inner functions can modify it


def w(Aligned_output, mid_lines, next_lines, sequence):
    predicted_structure = mid_lines[2]
    absolute_structure  = next_lines[1].lower()

    if len(predicted_structure) != len(absolute_structure):
        print("Error: Predicted and absolute structures must be of the same length!")
        return None

    match_c = match_h = match_e = 0

    for pred, abs_char in zip(predicted_structure, absolute_structure):
        if pred == abs_char:
            if pred == 'c':
                match_c += 1
            elif pred == 'h':
                match_h += 1
            elif pred == 'e':
                match_e += 1

    X = match_h
    Y = match_e
    Z = match_c
    Total_len   = len(sequence)
    Q3_accuracy = ((X + Y + Z) / Total_len) * 100 if Total_len > 0 else 0.0

    result_output = (
        f"No. of AAR correctly predicted in sec structure H: {X}\n"
        f"No. of AAR correctly predicted in sec structure E: {Y}\n"
        f"No. of AAR correctly predicted in sec structure C: {Z}\n"
        f"Total length of the sequence: {Total_len}\n"
        f"Q3 Accuracy: {Q3_accuracy:.2f}%"
    )

    return {
        "X":             X,
        "Y":             Y,
        "Z":             Z,
        "Q3_accuracy":   Q3_accuracy,
        "result_output": result_output,
    }


def _draw_graph(frame, idx):
    """Clear the frame and draw only the graph at index idx."""
    for widget in frame.winfo_children():
        widget.destroy()

    if not _graphs:
        return

    X, Y, Z, Q3_accuracy, label = _graphs[idx]
    total = len(_graphs)

    # ── Matplotlib figure ──────────────────────────────────────────────────
    fig = Figure(figsize=(5, 3.2), dpi=100)
    ax  = fig.add_subplot(111)

    categories = ['Helix (H)', 'Strand (E)', 'Coil (C)']
    values     = [X, Y, Z]

    sns.barplot(x=categories, y=values, palette=['#2196F3', '#F44336', '#4CAF50'], ax=ax)
    ax.axhline(
        y=Q3_accuracy, color='black', linestyle='--',
        label=f'Q3 Accuracy: {Q3_accuracy:.2f}%'
    )
    ax.set_xlabel('Secondary Structure Type')
    ax.set_ylabel('Correctly Predicted Residues')
    ax.set_title(
        f'Run {idx+1}/{total}  |  {label}  |  Q3: {Q3_accuracy:.2f}%',
        fontsize=9
    )
    ax.legend(fontsize=8)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    # ── Navigation bar ─────────────────────────────────────────────────────
    nav = tk.Frame(frame, bg="#ffffff")
    nav.pack(fill='x', pady=(2, 0))

    tk.Button(
        nav, text="◀  Prev",
        font=("Arial", 9, "bold"),
        bg="#e0e0e0", relief="flat", padx=8,
        state=tk.NORMAL if idx > 0 else tk.DISABLED,
        command=lambda: _go(frame, idx - 1)
    ).pack(side="left", padx=6, pady=3)

    tk.Label(
        nav,
        text=f"Graph {idx+1} of {total}",
        font=("Arial", 9), bg="#ffffff"
    ).pack(side="left", expand=True)

    tk.Button(
        nav, text="Next  ▶",
        font=("Arial", 9, "bold"),
        bg="#e0e0e0", relief="flat", padx=8,
        state=tk.NORMAL if idx < total - 1 else tk.DISABLED,
        command=lambda: _go(frame, idx + 1)
    ).pack(side="right", padx=6, pady=3)


def _go(frame, new_idx):
    _current_idx[0] = new_idx
    _draw_graph(frame, new_idx)


def plot(X, Y, Z, Q3_accuracy, frame, method_label=""):
    """
    Call every time user clicks Process.
    Appends to history, always shows the latest graph.
    Arrows let user browse previous runs.
    """
    _graphs.append((X, Y, Z, Q3_accuracy, method_label))
    latest = len(_graphs) - 1
    _current_idx[0] = latest
    _draw_graph(frame, latest)


def reset_graphs():
    """Optional: clear all graph history."""
    _graphs.clear()
    _current_idx[0] = 0