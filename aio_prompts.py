import csv
import sys
import datetime
from typing import List
from pathlib import Path
import pandas as pd
import logging
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory


# Prompt the user to choose whether to show the logging information or not
show_logs = input("Apakah anda inging melihat informasi logging? (y/n): ").lower() == 'y'

# Configure the logging module
logging.basicConfig(
    level=logging.INFO if show_logs else logging.WARNING,  # Set the logging level based on the user's input
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("payslip.log"),
        logging.StreamHandler(sys.stdout if show_logs else sys.stderr)  # Set the output stream based on the user's input
    ]
)

def input_data() -> str:
    today = datetime.date.today()
    filename = f"timbangan_{today}.csv"
    day_history = InMemoryHistory()
    plastic_type_history = InMemoryHistory()
    name_history = InMemoryHistory()

    logging.info(f"Opening CSV file for writing: {filename}")
    with open(filename, "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        rows = []
        count = 1  # Track current iteration number
        while True:
            # Function to print current iteration number
            def print_count():
                print(f"Data ke-{count}")

            print_count()  # Print current iteration number
            # Input name
            while True:
                name = prompt("Nama ('N'): ", history=name_history).strip().upper()
                if name == "N":
                    break
                elif name:
                    break
                else:
                    print("Harap masukkan nama.")
            
            if name == "N":
                choice = input("Tekan 'D' untuk menghapus baris terakhir\n"
                               "Tekan 'L' untuk melihat data saat ini\n"
                               "Tekan 'S' untuk menyimpan data dan keluar\n"
                               "Tekan 'C' untuk melanjutkan input data dari data terakhir\n"
                               "Pilihan: ").upper()
                if choice == "D":
                    if rows:
                        rows.pop()
                        print("Baris terakhir berhasil dihapus.")
                        logging.info("Last row deleted")
                    else:
                        print("Tidak ada baris yang dihapus.")
                        logging.warning("No row was deleted")
                elif choice == "L":
                    if rows:
                        for row in rows:
                            print(row)
                        logging.info("Showing current data")
                    else:
                        print("Tidak ada data saat ini.")
                        logging.info("No data available")
                elif choice == "S":
                    csv_writer.writerows(rows)
                    print("Data berhasil disimpan.")
                    logging.info("Data saved successfully")
                    return filename
                elif choice == "C":
                    if rows:
                        print("Melanjutkan input data dari data terakhir.")
                        logging.info("Continuing input data from last row")
                    else:
                        print("Tidak ada data sebelumnya.")
                        logging.info("No previous data available")
                else:
                    print("Pilihan tidak valid.")
                    logging.warning("Invalid choice selected")
            else:
                # Validate day input
                while True:
                    day = prompt("Masukkan Hari: ", history=day_history).strip().upper()
                    if day.isalpha():
                        break
                    else:
                        print("Input hari tidak valid. Harap masukkan hanya huruf.")

                # Input plastic type
                while True:
                    plastic_type = prompt("Jenis Plastik: ", history=plastic_type_history).strip().upper()
                    if plastic_type:
                        break
                    else:
                        print("Harap masukkan jenis plastik.")
                
                # Validate weight input
                while True:
                    weight = input("Timbangan (KG): ").strip()
                    try:
                        if "+" in weight:
                            weight = sum(map(float, weight.split("+")))
                        else:
                            weight = float(weight)
                        break
                    except ValueError:
                        print("Input timbangan tidak valid. Harap masukkan angka atau angka dengan tanda '+'")

                rows.append([name, day, plastic_type, weight])
                count += 1  # Increment iteration count

            day_history.append_string(day)
            plastic_type_history.append_string(plastic_type)
            name_history.append_string(name)

    return filename

def input_debts(df: pd.DataFrame) -> pd.DataFrame:
    today = datetime.date.today()
    debts_filename = f"debts_{today}.csv"
    logging.info(f"Opening debts file for writing: {debts_filename}")
    with open(debts_filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Name", "Debt", "Remaining Debt"])

        num_persons = input("Berapa banyak orang dengan BON? ")
        logging.info(f"Number of persons with debt: {num_persons}")
        if num_persons == "0":
            return df
        else:
            num_persons = int(num_persons)

        for i in range(num_persons):
            while True:
                name = input("Input Nama: ").upper()
                if name in df["Name"].values:
                    break
                else:
                    print("Nama orang tidak ditemukan.")
                    logging.warning(f"Name {name} not found in previous data")

            # Validate debt input
            while True:
                debt = input("BON (debt): ")
                try:
                    if "+" in debt:
                        debt = sum(map(float, debt.split("+")))
                    else:
                        debt = float(debt)
                    break
                except ValueError:
                    print("Input BON tidak valid. Harap masukkan angka atau angka dengan tanda '+'")
            
            # Validate remaining debt input
            while True:
                remaining_debt = input("Sisa BON (remaining debt): ")
                try:
                    if "+" in remaining_debt:
                        remaining_debt = sum(map(float, remaining_debt.split("+")))
                    else:
                        remaining_debt = float(remaining_debt)
                    break
                except ValueError:
                    print("Input sisa BON tidak valid. Harap masukkan angka atau angka dengan tanda '+'")

            if debt == 0:
                if "Debt" in df.columns:
                    df.loc[df["Name"] == name, "Debt"] = 0
                if "Remaining Debt" in df.columns:
                    df.loc[df["Name"] == name, "Remaining Debt"] = 0
            else:
                if "Debt" not in df.columns:
                    df["Debt"] = 0
                df.loc[df["Name"] == name, "Debt"] = debt
                if "Remaining Debt" not in df.columns:
                    df["Remaining Debt"] = 0
                df.loc[df["Name"] == name, "Remaining Debt"] = remaining_debt

            csv_writer.writerow([name, debt, remaining_debt])
            logging.info(f"Debt for {name}: {debt}, Remaining debt for {name}: {remaining_debt}")

    return df

def read_and_sort_csv(filename: str) -> pd.DataFrame:
    logging.info(f"Reading and sorting CSV file: {filename}")
    df = pd.read_csv(filename, names=["Name", "Day", "Plastic Type", "Weight (KG)"])
    df_sorted = df.sort_values(by=["Name"])
    logging.info(f"CSV file sorted and returned as DataFrame")
    return df_sorted

def calculate_salary(df: pd.DataFrame) -> pd.DataFrame:
    plastic_types = df["Plastic Type"].unique()
    price_map = {}
    for plastic_type in plastic_types:
        while True:
            price = input(f"Masukkan harga untuk {plastic_type}: ")
            try:
                price = float(price)
                break
            except ValueError:
                print("Input harga tidak valid. Harap masukkan angka")

        price_map[plastic_type] = price
        
    # Ask for confirmation to continue
    while True:
        confirm = input("Apakah harga sudah benar? (y/n): ")
        if confirm.lower() == "y":
            break
        elif confirm.lower() == "n":
            # Re-input plastic price
            for plastic_type in plastic_types:
                while True:
                    price = input(f"Masukkan harga untuk {plastic_type}: ")
                    try:
                        price = float(price)
                        break
                    except ValueError:
                        print("Input harga tidak valid. Harap masukkan angka")
                price_map[plastic_type] = price
            continue
        else:
            print("Input tidak valid. Harap masukkan 'y' atau 'n'")
        
    # Save price list to text file
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"stats_{today}.txt"
    logging.info(f"Opening price list file for writing: {filename}")
    with open(filename, "w") as f:
        # Write the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Date: {current_date}\n\n")

        # Write the plastic prices
        for plastic_type, price in price_map.items():
            f.write(f"{plastic_type}: {price}\n")

    logging.info(f"Price list saved to file: {filename}")

    df["Price (RP)"] = df["Plastic Type"].apply(lambda x: price_map.get(x, 300))
    df["Salary"] = df["Weight (KG)"] * df["Price (RP)"]
    logging.info(f"Salary calculated and returned as DataFrame")
    return df
    
def sum_weighted_plastics(df_agg):
    # Aggregate data by plastic type and sum the weight
    total_weighted_plastics = df_agg.groupby("Plastic Type")["Weight (KG)"].sum()
    return total_weighted_plastics

def rank_last_payment(df_agg):
    # Create a list of tuples containing name, last_payment, and rank
    last_payments = []
    for name in df_agg["Name"].unique():
        payslip = df_agg.loc[df_agg["Name"] == name]
        total_payment = payslip["Salary"].sum()
        if "Debt" in payslip.columns:
            debt = payslip.iloc[0]["Debt"]
        else:
            debt = pd.NA

        # Initialize last_payment with default value total_payment
        last_payment = total_payment

        # Update last_payment if the person has a debt
        if not pd.isna(debt):
            last_payment = total_payment - debt

        # Add name, last_payment, and rank to last_payments list
        last_payments.append((name, last_payment))

    # Sort the last_payments list in descending order based on last_payment
    last_payments_sorted = sorted(last_payments, key=lambda x: x[1], reverse=True)

    # Add rank to each entry in last_payments_sorted
    last_payments_ranked = [(i+1, name, last_payment) for i, (name, last_payment) in enumerate(last_payments_sorted)]
    return last_payments_ranked

def generate_stats(df_agg):
    # Get the current date for the filename
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Call sum_weighted_plastics function to get the weighted plastic totals
    total_weighted_plastics = sum_weighted_plastics(df_agg)

    # Call rank_last_payment function to get the ranked list of last payments
    last_payments_ranked = rank_last_payment(df_agg)

    # Save the lists to a text file
    filename = f"stats_{current_date}.txt"
    with open(filename, "a") as f:  # Use "a" to append to the file

        # Write total weighted plastics
        f.write("\nJumlah berat tiap plastik:\n")
        for plastic_type, total_weight in total_weighted_plastics.items():
            f.write(f"{plastic_type}: {total_weight}\n")

        # Write ranked last payments
        f.write("\nRanking jumlah pembayaran gaji:\n")
        for rank, name, last_payment in last_payments_ranked:
            f.write(f"{rank}. {name}: Rp {last_payment:.0f}\n")

    print(f"Stats appended to {filename}")

def main():
    logging.info("Starting Payslip Generator")

    filename = input_data()
    logging.info(f"Input data file: {filename}")

    df_sorted = read_and_sort_csv(filename)
    logging.info("CSV file read and sorted")

    df_salary = calculate_salary(df_sorted)
    logging.info("Salary calculated")

    # Aggregate data by name, day, and plastic type
    df_agg = df_salary.groupby(["Name", "Day", "Plastic Type"]).agg(
        {"Weight (KG)": "sum", "Salary": "sum"}
    ).reset_index()

    df_agg["Debt"] = pd.NA
    df_agg["Remaining Debt"] = pd.NA
    df_agg = input_debts(df_agg)
    logging.info("Debt information inputted")

    # Create a payslip markdown table for each person
    payslip_tables = []

    # Initialize variables to store sum of total payment slip, debt, and remaining debt
    sum_total_payment = 0
    sum_total_debt = 0
    sum_total_remaining_debt = 0
    sum_total_last_payment = 0

    # Create a list of tuples containing name and last_payment
    last_payments = []
    for name in df_agg["Name"].unique():
        payslip = df_agg.loc[df_agg["Name"] == name]
        total_payment = payslip["Salary"].sum()
        total_compensation = payslip.groupby(["Plastic Type"])["Salary"].sum()
        total_weight = payslip.groupby(["Plastic Type"])["Weight (KG)"].sum()
        if "Debt" in payslip.columns:
            debt = payslip.iloc[0]["Debt"]
        else:
            debt = pd.NA
        remaining_debt = payslip.iloc[0]["Remaining Debt"]
        
        # Initialize last_payment with default value total_payment
        last_payment = total_payment
        
        # Update last_payment if the person has a debt
        if not pd.isna(debt):
            last_payment = total_payment - debt
        
        # Add last_payment to sum_total_last_payment
        sum_total_last_payment += last_payment
        
        # Add name and last_payment to last_payments list
        last_payments.append((name, last_payment))

        # Create horizontal headings
        days = sorted(payslip["Day"].unique())
        horiz_headings = "|TIPE|" + "|".join(f"{day}" for day in days) + "| TTL | UPH (RP) |"
        horiz_divider = "|---"*(len(days)+3) + "|\n"

        # Create vertical headings and table rows
        vert_headings = sorted(payslip["Plastic Type"].unique())
        rows = []
        for plastic_type in vert_headings:
            row = f"|{plastic_type}|"
            for day in days:
                weight = payslip.loc[(payslip["Day"] == day) & (payslip["Plastic Type"] == plastic_type), "Weight (KG)"].sum()
                row += f"{weight}|"
            total_weight_type = total_weight.get(plastic_type, 0)
            compensation = total_compensation.get(plastic_type, 0)
            row += f"{total_weight_type}|{compensation}|"
            rows.append(row)

        # Create total row
        total_row = f"|Total|"
        for day in days:
            total_weight_day = payslip.loc[payslip["Day"] == day, "Weight (KG)"].sum()
            total_row += f"{total_weight_day}|"
        total_row += f"{total_weight.sum()}|{total_compensation.sum()}|"
        rows.append(total_row)

        # Combine all rows into a markdown table
        payslip_table = f"\n======***======\n"
        payslip_table += f"Nama: BU {name}\n"
        payslip_table += f"Tanggal: {datetime.date.today()}\n\n"
        payslip_table += horiz_headings + "\n"
        payslip_table += horiz_divider
        for i, row in enumerate(rows):
            payslip_table += row + "\n"
            if i == len(rows) - 2:
                payslip_table += horiz_divider
                # Update payslip table with new variables
        payslip_table += f"\nGaji: Rp {total_payment:.0f}"
        payslip_table += f"\nBON: Rp {debt:.0f}"
        payslip_table += f"\nSisa BON: Rp {remaining_debt:.0f}"
        payslip_table += f"\nGaji akhir: Rp {last_payment:.0f}"
        payslip_table += f"\n======***======"
        payslip_tables.append(payslip_table)

        # Update the sum of total payment slip, debt, and remaining debt
        sum_total_payment += total_payment
        if not pd.isna(debt):
            sum_total_debt += debt
        if not pd.isna(remaining_debt):
            sum_total_remaining_debt += remaining_debt

    # Sort the last_payments list in descending order based on last_payment
    last_payments_sorted = sorted(last_payments, key=lambda x: x[1], reverse=True)

    # Generate stats and save to file
    generate_stats(df_agg)

    # Print the sum of total payment slip, debt, remaining debt, and last payment
    logging.info("Generating summary of total payment slip, debt, remaining debt, and last payment")
    print(f"\n\nTotal Pembayaran Gaji: Rp {sum_total_payment:.0f}")
    print(f"Total BON: Rp {sum_total_debt:.0f}")
    print(f"Total Sisa BON: Rp {sum_total_remaining_debt:.0f}")
    print(f"Total Gaji Akhir: Rp {sum_total_last_payment:.0f}")

    # Save all the payslip tables to a text file
    logging.info("Saving payslip tables to text file")
    with open("payslips.txt", "w") as f:
        for payslip_table in payslip_tables:
            f.write(payslip_table)
            f.write("\n")
        # Insert sum of total payment slip, debt, remaining debt, and last payment into the payslips.txt file
        f.write(f"\n\nTotal Pembayaran Gaji: Rp {sum_total_payment:.0f}")
        f.write(f"\nTotal BON: Rp {sum_total_debt:.0f}")
        f.write(f"\nTotal Sisa BON: Rp {sum_total_remaining_debt:.0f}")
        f.write(f"\nTotal Gaji Akhir: Rp {sum_total_last_payment:.0f}")
        
    logging.info("Payslip generation complete [END]")

if __name__ == "__main__":
    main()

