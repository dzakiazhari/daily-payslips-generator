import os
import re
import difflib
import random
import string
import pandas as pd

def clear_cmd():
    # Clear command for Windows
    if os.name == 'nt':
        os.system('cls')
    # Clear command for Linux and macOS
    else:
        os.system('clear')

# Function to load the database from the .xlsx file
def load_database(filename):
    data = pd.read_excel(filename)
    return list(data['name']), list(data['day']), list(data['plastic_type'])

# Function to check if a value is a proper number
def is_value(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def find_closest_match(word, word_list):
    best_match = None
    best_distance = float('inf')
    
    for candidate in word_list:
        distance = levenshtein_distance(word, candidate)
        if distance < best_distance:
            best_distance = distance
            best_match = candidate
    
    return best_match if best_match else "NONE"

def levenshtein_distance(s1, s2):
    if isinstance(s1, str) and isinstance(s2, str):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    deletion = distances[i1] + 1
                    insertion = distances_[-1] + 1
                    substitution = distances[i1] + 1
                    distances_.append(min(deletion, insertion, substitution))
            distances = distances_

        return distances[-1]
    else:
        return float('inf')


# Function to handle timbangan files
def handle_timbangan_file(file_path, names, days, plastic_types):
    file_name = os.path.basename(file_path)
    errors = []
    with open(file_path, 'r') as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if line:
                row = line.split(',')
                if len(row) == 4:
                    name, day, plastic_type, weight = row
                    mismatch_reasons = []
                    if name not in names:
                        mismatch_reasons.append("NAMA TIDAK COCOK")
                        name_suggestion = find_closest_match(name, names)
                        if name_suggestion != "NONE":
                            mismatch_reasons.append(f"Saran: {name_suggestion}")
                    if day not in days:
                        mismatch_reasons.append("HARI TIDAK COCOK")
                        day_suggestion = find_closest_match(day, days)
                        if day_suggestion != "NONE":
                            mismatch_reasons.append(f"Saran: {day_suggestion}")
                    if plastic_type not in plastic_types:
                        mismatch_reasons.append("JENIS PLASTIK TIDAK COCOK")
                        plastic_type_suggestion = find_closest_match(plastic_type, plastic_types)
                        if plastic_type_suggestion != "NONE":
                            mismatch_reasons.append(f"Saran: {plastic_type_suggestion}")
                    if not is_value(weight):
                        mismatch_reasons.append("BERAT TIDAK VALID")
                    if mismatch_reasons:
                        error = f"Baris No.{line_num} {row} REASON: {', '.join(mismatch_reasons)}"
                        errors.append(error)
                else:
                    error = f"Baris No.{line_num} {row} REASON: INVALID ROW FORMAT"
                    errors.append(error)
    return file_name, errors

# Function to handle debt files
def handle_debt_file(file_path, names):
    file_name = os.path.basename(file_path)
    errors = []
    with open(file_path, 'r') as file:
        next(file)  # Skip header
        for line_num, line in enumerate(file, start=2):
            line = line.strip()
            if line:
                row = line.split(',')
                if len(row) == 3:
                    name, debt, remaining_debt = row
                    mismatch_reasons = []
                    if name not in names:
                        mismatch_reasons.append("NAMA TIDAK COCOK")
                        name_suggestion = find_closest_match(name, names)
                        if name_suggestion != "NONE":
                            mismatch_reasons.append(f"Saran: {name_suggestion}")
                    if not is_value(debt):
                        mismatch_reasons.append("HUTANG TIDAK VALID")
                    if not is_value(remaining_debt):
                        mismatch_reasons.append("SISA HUTANG TIDAK VALID")
                    if mismatch_reasons:
                        error = f"Baris No.{line_num} {row} REASON: {', '.join(mismatch_reasons)}"
                        errors.append(error)
                else:
                    error = f"Baris No.{line_num} {row} REASON: INVALID ROW FORMAT"
                    errors.append(error)
    return file_name, errors

# Function to handle directory and files
def handle_directory(folder_path, database_path):
    # Load database
    names, days, plastic_types = load_database(database_path)

    # Get list of .csv files in the folder
    files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    timbangan_files = [file for file in files if file.startswith('timbangan')]
    debt_files = [file for file in files if file.startswith('debt')]

    # Check if folder is empty
    if not files:
        print("Folder is empty.")
        return

    report = []  # Define the report list to store the results
    total_missinputs = 0  # Initialize total_missinputs variable

    # Handle timbangan files
    if not timbangan_files:
        print("No timbangan files found.")
    else:
        for file in timbangan_files:
            file_path = os.path.join(folder_path, file)
            file_name, errors = handle_timbangan_file(file_path, names, days, plastic_types)
            report.append((file_name, errors))
            total_missinputs += len(errors)

    # Handle debt files
    if not debt_files:
        print("No debt files found.")
    else:
        for file in debt_files:
            file_path = os.path.join(folder_path, file)
            file_name, errors = handle_debt_file(file_path, names)
            report.append((file_name, errors))

            total_missinputs += len(errors)

    # Generate random hex code
    random_hex = ''.join(random.choices(string.hexdigits, k=8))

    # Write report to file
    report_filename = f"cek_input_{random_hex}.txt"
    report_filepath = os.path.join(folder_path, report_filename)
    with open(report_filepath, 'w') as file:
        file.write(f"Daftar File: {files}\n\n")

        for file_name, errors in report:
            file.write(f"Nama FILE: {file_name}\n")
            
            for i, error in enumerate(errors, start=1):
                file.write(f"{i}: {error}\n")  # Use the inner loop's enumerate counter (i) for numbering
            file.write("\n")

        file.write(f"Jumlah file yang diperiksa: {len(files)}\n")
        file.write(f"Jumlah kesalahan: {total_missinputs}\n")
        file.write(f"File disimpan ke \"{report_filepath}\"\n")

    print("Laporan berhasil dihasilkan.")
    print(f"File disimpan sebagai \"{report_filename}\" di direktori {folder_path}.")

    # Mencetak laporan ke terminal
    with open(report_filepath, 'r') as file:
        print(file.read())

# Main function
def main():
    clear_cmd()
    folder_path = "INPUT"  # Change this to the actual folder path
    database_path = "database.xlsx"  # Change this to the actual database path

    if os.path.exists(folder_path) and os.path.exists(database_path):
        handle_directory(folder_path, database_path)
    else:
        print("Folder atau database tidak ditemukan.")

if __name__ == "__main__":
    main()