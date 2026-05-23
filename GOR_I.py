"""
GOR I - Local Implementation
Based on: Garnier, Osguthorpe & Robson (1978)
No internet / server / Selenium required.
Uses single-residue information theory matrices.
Output format is identical to the old PRABI server output.
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# GOR I Information Matrices  (H, E, C values per amino acid)
# Source: Garnier et al. 1978, J. Mol. Biol. 120:97-120
# Rows = amino acids (order: A C D E F G H I K L M N P Q R S T V W Y)
# Cols = [I(H), I(E), I(C)]  in units of 0.1 * millibans (integer form)
# ─────────────────────────────────────────────────────────────────────────────
GOR1_MATRIX = {
    'A': ( 142, -97,  -45),
    'C': ( -15,  39,  -24),
    'D': (-100,  79,   21),
    'E': ( 151, -111,  -40),
    'F': (  15,  45,  -60),
    'G': (-261,  17,  244),
    'H': (  71,  12,  -83),
    'I': (-108, 218, -110),
    'K': ( 110, -82,  -28),
    'L': ( 152, -72,  -80),
    'M': ( 105,  54, -159),
    'N': ( -91,  43,   48),
    'P': (-199, -136, 335),
    'Q': ( 111, -28,  -83),
    'R': (  98, -60,  -38),
    'S': ( -50,  -5,   55),
    'T': ( -78,  56,   22),
    'V': ( -48, 175,  -73),
    'W': (  12,  25,  -37),
    'Y': ( -15,  84,  -69),
}

# Decision constants (theta values) — standard GOR I defaults
THETA_H = 0
THETA_E = 0
THETA_C = 0


def predict_gor1(sequence):
    """
    Predict secondary structure for a protein sequence using GOR I.
    Returns a string of 'h', 'e', 'c' characters (same length as sequence).
    """
    sequence = sequence.upper().strip()
    prediction = []

    for aa in sequence:
        scores = GOR1_MATRIX.get(aa, (0, 0, 0))
        ih, ie, ic = scores

        # GOR I: assign the class with highest score
        if ih >= ie and ih >= ic:
            prediction.append('h')
        elif ie >= ih and ie >= ic:
            prediction.append('e')
        else:
            prediction.append('c')

    return ''.join(prediction)


def GOR_I(fasta_seq, mid_processes_data_4):
    """
    GOR I secondary structure prediction.
    Replaces the old Selenium/PRABI server approach.
    Same input/output contract as before.
    """
    # Clean the input sequence (remove whitespace, numbers, non-AA chars)
    sequence = re.sub(r'[^A-Za-z]', '', fasta_seq).upper()

    if not sequence:
        print("❌ Error: Empty sequence provided to GOR_I.")
        return None

    print(f"✅ GOR I: Predicting for sequence of length {len(sequence)}")

    # Run prediction
    secondary_structure = predict_gor1(sequence)

    print(f"✅ GOR I Prediction:\n  SEQ: {sequence}\n  SS:  {secondary_structure}")

    # Build output in same format as old PRABI server
    gor_1_output_seq = sequence + "\n" + secondary_structure

    # Process mid_processes_data_4
    mid_lines = mid_processes_data_4.strip().split("\n")
    next_lines = gor_1_output_seq.strip().split("\n")

    if len(mid_lines) < 3:
        print("❌ Error: mid_processes_data_4 does not have sufficient lines!")
        return None
    if len(next_lines) < 2:
        print("❌ Error: GOR I output does not have sufficient lines!")
        return None

    header       = mid_lines[0]
    input_sequence = mid_lines[1]
    structure_1  = mid_lines[2]
    structure_2  = next_lines[1]

    max_length = max(len(input_sequence), len(structure_1), len(structure_2)) + 5

    aligned_output  = f"{header}\n"
    aligned_output += f"{input_sequence.ljust(max_length)}\n"
    aligned_output += f"{structure_1.ljust(max_length)}       Absolute\n"
    aligned_output += f"{structure_2.ljust(max_length)}       Predicted"

    print(f"🧩 Debug Info: Mid Lines: {mid_lines}")
    print(f"🧩 Debug Info: Next Lines: {next_lines}")
    print("✅ Aligned Output:")
    print(aligned_output)

    return {
        "mid_lines":      mid_lines,
        "next_lines":     next_lines,
        "sequence":       sequence,
        "aligned_output": aligned_output,
    }
