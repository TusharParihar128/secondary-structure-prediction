import requests
import re


def fetch_pdb_sequence(pdb_id):
    pdb_id = pdb_id.strip().upper()

    if not pdb_id:
        print("Error: PDB ID is empty.")
        return "Error: PDB ID cannot be empty."

    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            fasta_data = response.text
            # Remove header lines and join sequence
            fasta_sequence = re.sub(r">.*\n", "", fasta_data).replace("\n", "")
            print(f"\nSequence for {pdb_id}: {fasta_sequence}")
            return fasta_sequence
        else:
            error_message = f"Error: Unable to fetch PDB {pdb_id} (HTTP {response.status_code})"
            print(error_message)
            return error_message

    except requests.exceptions.RequestException as e:
        error_message = f"Error: Network issue occurred while fetching PDB: {e}"
        print(error_message)
        return error_message
