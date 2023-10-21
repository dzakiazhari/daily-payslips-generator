import csv
import os
import sys
import datetime
from typing import List
from pathlib import Path
import pandas as pd
import logging
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

def read_debts(filename: str) -> pd.DataFrame:
    debts = pd.read_csv(filename, names=["Name", "Debt", "Remaining Debt"])
    return debts.set_index("Name")

def merge_debts(df: pd.DataFrame, debts: pd.DataFrame) -> pd.DataFrame:
    df["Debt"] = df["Name"].apply(lambda x: debts.loc[x, "Debt"] if x in debts.index else 0)
    df["Remaining Debt"] = df["Name"].apply(lambda x: debts.loc[x, "Remaining Debt"] if x in debts.index else 0)
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
    ######    
    # Save price list to text file
    folder_name = "REVISI"
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = os.path.join(folder_name, f"rev_stats_{current_date}.txt")
    with open(filename, "a") as f:  # Use "a" to append to the file
        # Write the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        f.write(f"Tanggal: {current_date}\n")
        f.write(f"Harga Plastik: \n")
        
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
            debt = pd.to_numeric(payslip.iloc[0]["Debt"], errors="coerce")
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
    total_all_plastics = df_agg["Weight (KG)"].sum()
    total_weighted_plastics = sum_weighted_plastics(df_agg)
    last_payments_ranked = rank_last_payment(df_agg)

    # Calculate total weight of plastic for each person
    total_weight_per_person = df_agg.groupby("Name")["Weight (KG)"].sum()

    # Sort last payments ranked by highest last payment
    last_payments_ranked.sort(key=lambda x: x[2], reverse=True)

    # Save the lists to a text file
    folder_name = "REVISI"

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Get the current date for the filename
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(folder_name, f"rev_stats_{current_date}.txt")

    with open(filename, "a") as f:  # Use "a" to append to the file
        # Write total weighted plastics
        f.write(f"\nTotal berat seluruh plastik: {total_all_plastics} kg")
        f.write("\nJumlah berat tiap plastik:\n")
        for plastic_type, total_weight in total_weighted_plastics.items():
            f.write(f"{plastic_type}: {total_weight}\n")

        # Write ranked last payments with weight
        f.write("\nRanking jumlah pembayaran gaji:\n")
        for rank, name, last_payment in last_payments_ranked:
            rank_weight = total_weight_per_person.get(name, 0)
            f.write(f"{rank}. {name}: Rp {last_payment:.0f} | {rank_weight} kg\n")

    print(f"Stats appended to {filename}")

def main():
    logging.info("Starting Payslip Generator")

    today = datetime.date.today()
    input_folder = "INPUT"
    timbangan_filename = os.path.join(input_folder, f"timbangan_{today}.csv")
    payment_filename = os.path.join(input_folder, f"debts_{today}.csv")
    
    df_sorted = read_and_sort_csv(timbangan_filename)
    df_salary = calculate_salary(df_sorted)

    # Aggregate data by name, day, and plastic type
    df_agg = df_salary.groupby(["Name", "Day", "Plastic Type"]).agg(
        {"Weight (KG)": "sum", "Salary": "sum"}
    ).reset_index()


    df_agg["Debt"] = pd.NA
    df_agg["Remaining Debt"] = pd.NA
    debts = read_debts(payment_filename)
    df_agg = merge_debts(df_agg, debts)
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
            debt = pd.to_numeric(payslip.iloc[0]["Debt"], errors="coerce")
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
        payslip_table = f"\n============***============\n"
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
        payslip_table += f"\nSisa BON: Rp {float(remaining_debt):.0f}"
        payslip_table += f"\nGaji akhir: Rp {last_payment:.0f}"
        payslip_table += f"\n============***============"
        payslip_tables.append(payslip_table)

        # Update the sum of total payment slip, debt, and remaining debt
        sum_total_payment += total_payment
        if not pd.isna(debt):
            sum_total_debt += debt
        if not pd.isna(remaining_debt):
            sum_total_remaining_debt += float(remaining_debt)

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
    #####
    # Save all the payslip tables to a text file
    logging.info("Saving payslip tables to text file")
    folder_name = "REVISI"
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = os.path.join(folder_name, f"rev_payslips_{current_date}.txt")
    with open(filename, "a") as f:  # Use "a" to append to the file
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

