import re


# Step 1: Modify secondary structure
def modify_secondary_structure(input_data):
    lines = input_data.strip().split("\n")
    num_lines = []
    sec_lines = []

    for i, line in enumerate(lines):
        line = line.expandtabs()
        if any(c.isalpha() for c in line) and any(c.isdigit() for c in line[:5]):
            num_lines.append(i)
        elif any(c.isalpha() for c in line):
            sec_lines.append(i)

    if not num_lines:
        return "Invalid input format"

    for num_index in num_lines:
        numeric_string = lines[num_index].expandtabs()
        sequence = "".join([c if c.isalpha() else " " for c in numeric_string])
        last_alpha_index = max(i for i, c in enumerate(sequence) if c.isalpha())
        actual_insert_index = last_alpha_index + 1
        corresponding_sec_index = next((i for i in sec_lines if i > num_index), None)

        if corresponding_sec_index is not None:
            secondary_string = lines[corresponding_sec_index].expandtabs()
            if len(secondary_string) < actual_insert_index + 1:
                secondary_string = secondary_string.ljust(actual_insert_index + 1)
            modified_sec = secondary_string[:actual_insert_index] + "C" + secondary_string[actual_insert_index + 1:]
            lines[corresponding_sec_index] = modified_sec

    return "\n".join(lines)


# Step 2: Process sequence data
def process_sequence_data(input_data):
    lines = input_data.split("\n")
    processed_lines = []
    last_numeric_line = None
    last_numeric_index = None
    first_alpha_index = None
    last_alpha_index = None

    for index, line in enumerate(lines):
        if line.strip():
            normalized_line = line.expandtabs()
            parts = normalized_line.split()
            if parts[0].isdigit():
                last_numeric_line = normalized_line
                last_numeric_index = index
                seq_part = " ".join(parts[1:]) if len(parts) > 1 else ""
                first_alpha_index = normalized_line.find(next((c for c in seq_part if c.isalpha()), "a"))
                last_alpha_index = normalized_line.rfind(seq_part.rstrip()[-1]) + 1

    for index, line in enumerate(lines):
        processed_lines.append(line.expandtabs())
        if index == last_numeric_index:
            filler_line = " " * first_alpha_index + "c" * (last_alpha_index - first_alpha_index)
            processed_lines.append(filler_line)

    return "\n".join(processed_lines)


# Step 3: Main function
def main_function(input_data):
    lines = input_data.split("\n")
    num_lines = []
    sec_lines = []

    for i, line in enumerate(lines):
        line = line.expandtabs()
        if any(c.isalpha() for c in line) and any(c.isdigit() for c in line[:5]):
            num_lines.append(i)
        elif any(c.isalpha() for c in line):
            sec_lines.append(i)

    if not num_lines:
        return "Invalid input format: No numeric lines found."

    last_num_index = num_lines[-1]
    non_numeric_after_last_numeric = False
    for index in range(last_num_index + 1, len(lines)):
        if index in sec_lines:
            non_numeric_after_last_numeric = True
            break

    if non_numeric_after_last_numeric:
        result = modify_secondary_structure(input_data)
    else:
        processed_data = process_sequence_data(input_data)
        result = modify_secondary_structure(processed_data)

    return result


# Step 4: DSSP processing
def process_dssp(input_data):
    lines = input_data.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        line = line.expandtabs()
        if line and line[0].isdigit():
            first_alpha_idx = next((j for j, char in enumerate(line) if char.isalpha()), None)
            last_alpha_idx = max((j for j, char in enumerate(line) if char.isalpha()), default=None)

            if first_alpha_idx is not None and last_alpha_idx is not None:
                new_line = list(line)
                for j in range(first_alpha_idx, last_alpha_idx + 1):
                    if new_line[j] == ' ':
                        new_line[j] = 'c'
                new_lines.append(''.join(new_line))
            else:
                new_lines.append(line)
        else:
            if i > 0 and new_lines and new_lines[-1][0].isdigit():
                numeric_line = new_lines[-1]
                first_alpha_idx = next((j for j, char in enumerate(numeric_line) if char.isalpha()), None)
                last_alpha_idx = max((j for j, char in enumerate(numeric_line) if char.isalpha()), default=None)

                if first_alpha_idx is not None and last_alpha_idx is not None:
                    new_line = list(line)
                    for j in range(len(new_line)):
                        if first_alpha_idx <= j <= last_alpha_idx:
                            if new_line[j] == ' ' or new_line[j] == 'T':
                                new_line[j] = 'c'
                    new_lines.append(''.join(new_line))
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

    new_dssp = '\n'.join(new_lines)
    sections = new_dssp.split('\n')
    processed_sections = []
    for section in sections:
        if section and not section[0].isdigit():
            section = list(section)
            for j in range(len(section) - 1, -1, -1):
                if section[j] == 'C':
                    section.pop(j)
                    break
            processed_sections.append(''.join(section))
        else:
            processed_sections.append(section)

    return '\n'.join(processed_sections)


# Step 5: Remove stars
def remove_stars(input_data):
    lines = input_data.split("\n")
    processed_lines = []

    for i in range(len(lines)):
        line = lines[i]
        if re.match(r"^\s*\d+", line):
            count = 0
            new_line = ""
            for char in line:
                if char.isalnum():
                    count += 1
                if count > 10 and char == "c":
                    continue
                new_line += char
            processed_lines.append(new_line)
        else:
            count = 0
            new_line = ""
            for char in line:
                if char.isalpha() or char == 'c':
                    count += 1
                if count > 10 and char == 'c':
                    count = 0
                    continue
                new_line += char.lower()
            processed_lines.append(new_line)

    return "\n".join(processed_lines)


def clean_lines(input_data):
    processed_lines = []
    for line in input_data.split("\n"):
        line = re.sub(r"^\d+\s*", "", line)
        line = line.lstrip()
        processed_lines.append(line)
    return "\n".join(processed_lines)


def process_cleaned_data(input_data):
    mid_processes_data_3 = [line.strip() for line in input_data.strip().split("\n") if line.strip()]

    if len(mid_processes_data_3) < 2:
        print("Error: cleaned_result me sufficient lines nahi hain! Check karo!")
        return None

    forward_2 = [mid_processes_data_3[0]]
    sequence = ""
    secondary_structure = ""

    for i in range(1, len(mid_processes_data_3)):
        if i % 2 == 1:
            sequence += mid_processes_data_3[i]
        else:
            secondary_structure += mid_processes_data_3[i]

    forward_2.append(sequence)
    forward_2.append(secondary_structure)

    mid_processes_data_4 = "\n".join(forward_2)
    return mid_processes_data_4


# Full pipeline
def process_dssp_pipeline(input_data):
    processed1 = modify_secondary_structure(input_data)
    processed2 = process_sequence_data(processed1)
    processed3 = main_function(input_data)
    processed4 = process_dssp(processed3)
    processed5 = remove_stars(processed4)
    processed6 = clean_lines(processed5)
    processed7 = process_cleaned_data(processed6)
    return processed7
