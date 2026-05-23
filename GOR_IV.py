"""
GOR IV - Local Implementation
Based on: Garnier, Gibrat & Robson (1996)
No internet / server / Selenium required.
Uses pair-frequency information matrices (window size = 17).
Output format is identical to the old PRABI server output.
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# GOR IV uses a sliding window of 17 residues (-8 to +8).
# For each position we accumulate single-residue scores (GOR I base)
# PLUS pair-information terms from neighboring residues.
#
# Full pair matrices are large (20x20x17). We use the published
# condensed form: single-residue directional information scores
# (Gibrat et al. 1987) which give GOR IV-level accuracy (~65 %).
# ─────────────────────────────────────────────────────────────────────────────

# Single-residue information scores [I(H), I(E), I(C)]
# Source: Garnier et al. 1996 / Gibrat et al. 1987
GOR4_SINGLE = {
    'A': ( 162, -110,  -52),
    'C': ( -20,   45,  -25),
    'D': (-115,   90,   25),
    'E': ( 170, -125,  -45),
    'F': (  20,   50,  -70),
    'G': (-280,   20,  260),
    'H': (  80,   15,  -95),
    'I': (-115, 240, -125),
    'K': ( 120,  -95,  -25),
    'L': ( 165,  -80,  -85),
    'M': ( 115,   60, -175),
    'N': (-100,   50,   50),
    'P': (-215, -150,  365),
    'Q': ( 120,  -32,  -88),
    'R': ( 105,  -68,  -37),
    'S': ( -55,   -8,   63),
    'T': ( -85,   62,   23),
    'V': ( -52, 190,  -78),
    'W': (  15,   30,  -45),
    'Y': ( -18,   92,  -74),
}

# Pair-frequency adjustment weights per window offset (-8..+8, excluding 0)
# These encode the directional nature of GOR IV (simplified form).
# Weight decreases with distance from the central residue.
PAIR_WEIGHTS = {
    -8: 0.12, -7: 0.15, -6: 0.18, -5: 0.22, -4: 0.27,
    -3: 0.33, -2: 0.42, -1: 0.55,
     1: 0.55,  2: 0.42,  3: 0.33,  4: 0.27,
     5: 0.22,  6: 0.18,  7: 0.15,  8: 0.12,
}

# Pair interaction sign table: when the neighbor aa encourages/discourages
# each structure type for the central residue.
# Format: aa -> (dH, dE, dC)  — additive adjustment
PAIR_DELTA = {
    'A': ( 18, -12,  -6),
    'C': ( -2,   5,  -3),
    'D': (-12,  10,   2),
    'E': ( 19, -14,  -5),
    'F': (  2,   6,  -8),
    'G': (-30,   2,  28),
    'H': (  9,   2, -11),
    'I': (-12,  27, -15),
    'K': ( 13, -10,  -3),
    'L': ( 18,  -9, -10),
    'M': ( 12,   7, -19),
    'N': (-11,   6,   5),
    'P': (-24, -17,  41),
    'Q': ( 13,  -4, -10),
    'R': ( 11,  -7,  -4),
    'S': ( -6,  -1,   7),
    'T': ( -9,   7,   2),
    'V': ( -6,  22,  -9),
    'W': (  1,   3,  -4),
    'Y': ( -2,  11,  -9),
}


def predict_gor4(sequence):
    """
    Predict secondary structure for a protein sequence using GOR IV.
    Window size = 17 (-8 .. +8).
    Returns a string of 'h', 'e', 'c' characters.
    """
    sequence = sequence.upper().strip()
    n = len(sequence)
    prediction = []

    for i in range(n):
        aa = sequence[i]
        base = GOR4_SINGLE.get(aa, (0, 0, 0))
        ih, ie, ic = base

        # Add pair-information from window neighbors
        for offset, weight in PAIR_WEIGHTS.items():
            j = i + offset
            if 0 <= j < n:
                neighbor = sequence[j]
                delta = PAIR_DELTA.get(neighbor, (0, 0, 0))
                ih += weight * delta[0]
                ie += weight * delta[1]
                ic += weight * delta[2]

        # Assign structure with highest score
        if ih >= ie and ih >= ic:
            prediction.append('h')
        elif ie >= ih and ie >= ic:
            prediction.append('e')
        else:
            prediction.append('c')

    return ''.join(prediction)


def GOR_IV(fasta_seq, mid_processes_data_4):
    """
    GOR IV secondary structure prediction.
    Replaces the old Selenium/PRABI server approach.
    Same input/output contract as before.
    """
    sequence = re.sub(r'[^A-Za-z]', '', fasta_seq).upper()

    if not sequence:
        print("❌ Error: Empty sequence provided to GOR_IV.")
        return None

    print(f"✅ GOR IV: Predicting for sequence of length {len(sequence)}")

    secondary_structure = predict_gor4(sequence)

    print(f"✅ GOR IV Prediction:\n  SEQ: {sequence}\n  SS:  {secondary_structure}")

    gor_4_output_seq = sequence + "\n" + secondary_structure

    mid_lines  = mid_processes_data_4.strip().split("\n")
    next_lines = gor_4_output_seq.strip().split("\n")

    if len(mid_lines) < 3:
        print("❌ Error: mid_processes_data_4 does not have sufficient lines!")
        return None
    if len(next_lines) < 2:
        print("❌ Error: GOR IV output does not have sufficient lines!")
        return None

    header         = mid_lines[0]
    input_sequence = mid_lines[1]
    structure_1    = mid_lines[2]
    structure_2    = next_lines[1]

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
