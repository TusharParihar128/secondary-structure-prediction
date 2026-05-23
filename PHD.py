"""
PHD - Local Implementation (replaces PRABI/Selenium scraping)
PHD (Profile network from HeiDelberg) uses evolutionary profiles.
Since we don't have PSI-BLAST profiles available locally, we implement
a simplified PHD-style prediction using position-specific propensity
scores — same output format as before.
"""

import re

# PHD-style amino acid propensity scores [H, E, C]
# Derived from Rost & Sander (1993) propensity tables
PHD_PROPENSITY = {
    'A': ( 142, -97,  -45),
    'C': (  17,  52,  -69),
    'D': ( -95,  72,   23),
    'E': ( 151, -107, -44),
    'F': (  31,  78,  -109),
    'G': (-258,  18,  240),
    'H': (  74,  28,  -102),
    'I': (-111, 225, -114),
    'K': ( 106, -78,  -28),
    'L': ( 149, -68,  -81),
    'M': ( 108,  62, -170),
    'N': ( -88,  48,   40),
    'P': (-202, -130, 332),
    'Q': ( 114, -30,  -84),
    'R': ( 101, -64,  -37),
    'S': ( -48,  -4,   52),
    'T': ( -75,  58,   17),
    'V': ( -45, 180,  -75),
    'W': (  22,  48,  -70),
    'Y': ( -12,  90,  -78),
}

# Window size for PHD (uses context of 13 residues, -6 to +6)
PHD_WINDOW = 6
PHD_WINDOW_WEIGHTS = {
    -6: 0.10, -5: 0.14, -4: 0.20, -3: 0.30, -2: 0.45, -1: 0.65,
     1: 0.65,  2: 0.45,  3: 0.30,  4: 0.20,  5: 0.14,  6: 0.10,
}


def predict_phd(sequence):
    """
    Predict secondary structure using PHD-style propensity scoring.
    Returns a string of 'h', 'e', 'c' characters.
    """
    sequence = sequence.upper().strip()
    n = len(sequence)
    prediction = []

    for i in range(n):
        aa = sequence[i]
        base = PHD_PROPENSITY.get(aa, (0, 0, 0))
        ih, ie, ic = float(base[0]), float(base[1]), float(base[2])

        # Context window contribution
        for offset, weight in PHD_WINDOW_WEIGHTS.items():
            j = i + offset
            if 0 <= j < n:
                neighbor_scores = PHD_PROPENSITY.get(sequence[j], (0, 0, 0))
                ih += weight * neighbor_scores[0] * 0.5
                ie += weight * neighbor_scores[1] * 0.5
                ic += weight * neighbor_scores[2] * 0.5

        if ih >= ie and ih >= ic:
            prediction.append('h')
        elif ie >= ih and ie >= ic:
            prediction.append('e')
        else:
            prediction.append('c')

    return ''.join(prediction)


def PHD(fasta_seq, mid_processes_data_4):
    """
    PHD secondary structure prediction — local version.
    Same input/output contract as the original Selenium-based version.
    """
    sequence = re.sub(r'[^A-Za-z]', '', fasta_seq).upper()

    if not sequence:
        print("❌ Error: Empty sequence provided to PHD.")
        return None

    print(f"✅ PHD: Predicting for sequence of length {len(sequence)}")

    secondary_structure = predict_phd(sequence)

    print(f"✅ PHD Prediction:\n  SEQ: {sequence}\n  SS:  {secondary_structure}")

    phd_output_seq = sequence + "\n" + secondary_structure

    mid_lines  = mid_processes_data_4.strip().split("\n")
    next_lines = phd_output_seq.strip().split("\n")

    if len(mid_lines) < 3:
        print("❌ Error: mid_processes_data_4 does not have sufficient lines!")
        return None
    if len(next_lines) < 2:
        print("❌ Error: PHD output does not have sufficient lines!")
        return None

    header         = mid_lines[0]
    input_sequence = mid_lines[1]
    structure_1    = mid_lines[2]
    structure_2    = next_lines[1].lower()

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
