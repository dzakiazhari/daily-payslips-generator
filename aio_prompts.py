import csv
import datetime
from typing import List
from pathlib import Path
import pandas as pd
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

def input_data() -> str:
    today = datetime.date.today()
    filename = f"timbangan_{today}.csv"
    name_history = InMemoryHistory()
    day_history = InMemoryHistory()
    plastic_type_history = InMemoryHistory()

    with open(filename, "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        rows = []
        while True:
            name = prompt("Nama ('N'): ", history=name_history).upper()
            if name == "N":
                choice = input("Tekan 'D' untuk menghapus baris terakhir\n"
                               "Tekan 'L' untuk melihat data saat ini\n"
                               "Tekan 'C' untuk melanjutkan input data dari data terakhir\n"
                               "Tekan 'S' untuk menyimpan data dan keluar\n"
                               "Pilihan: ").upper()
                if choice == "D":
                    if rows:
                        rows.pop()
                        print("Baris terakhir berhasil dihapus.")
                    else:
                        print("Tidak ada baris yang dihapus.")
                elif choice == "L":
                    if rows:
                        for row in rows:
                            print(row)
                    else:
                        print("Tidak ada data saat ini.")
                elif choice == "S":
                    csv_writer.writerows(rows)
                    print("Data berhasil disimpan.")
                    return filename
                elif choice == "C":
                    if rows:
                        print("Melanjutkan input data dari data terakhir.")
                    else:
                        print("Tidak ada data sebelumnya.")
                else:
                    print("Pilihan tidak valid.")
            else:
                day = prompt("Masukkan Hari: ", history=day_history).upper()
                plastic_type = prompt("Jenis Plastik: ", history=plastic_type_history).upper()
                weight = input("Timbangan (KG): ")

                if "+" in weight:
                    weight = sum(map(float, weight.split("+")))
                elif "." in weight:
                    weight = float(weight)
                else:
                    weight = int(weight)

                rows.append([name, day, plastic_type, weight])

            name_history.append_string(name.upper())
            day_history.append_string(day.upper())
            plastic_type_history.append_string(plastic_type.upper())
            
    return filename

def input_debts(df: pd.DataFrame) -> pd.DataFrame:
    today = datetime.date.today()
    debts_filename = f"payment_{today}.csv"

    with open(debts_filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Name", "Debt", "Remaining Debt"])

        num_persons = input("Berapa banyak orang dengan BON? ")
        if num_persons == "0":
            return df
        else:
            num_persons = int(num_persons)

        for i in range(num_persons):
            name = input("Input Nama: ").upper()
            debt = input("BON (debt): ")
            remaining_debt = input("Sisa BON (remaining debt): ")

            if debt == "0":
                if "Debt" in df.columns:
                    df.loc[df["Name"] == name, "Debt"] = 0
                if "Remaining Debt" in df.columns:
                    df.loc[df["Name"] == name, "Remaining Debt"] = 0
            else:
                if "Debt" not in df.columns:
                    df["Debt"] = 0
                df.loc[df["Name"] == name, "Debt"] = int(debt)
                if "Remaining Debt" not in df.columns:
                    df["Remaining Debt"] = 0
                df.loc[df["Name"] == name, "Remaining Debt"] = int(remaining_debt)

            csv_writer.writerow([name, debt, remaining_debt])

    return df


def read_and_sort_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename, names=["Name", "Day", "Plastic Type", "Weight (KG)"])
    df_sorted = df.sort_values(by=["Name"])
    return df_sorted

def calculate_salary(df: pd.DataFrame) -> pd.DataFrame:
    plastic_types = df["Plastic Type"].unique()
    price_map = {}
    for plastic_type in plastic_types:
        price = int(input(f"Masukkan harga untuk {plastic_type}: "))
        price_map[plastic_type] = price

    # Save price list to text file
    today = datetime.date.today()
    filename = f"price_list_{today}.txt"
    with open(filename, "w") as f:
        for plastic_type, price in price_map.items():
            f.write(f"{plastic_type}: {price}\n")
    
    df["Price (RP)"] = df["Plastic Type"].apply(lambda x: price_map.get(x, 300))
    df["Salary"] = df["Weight (KG)"] * df["Price (RP)"]
    return df


def main():
    filename = input_data()
    df_sorted = read_and_sort_csv(filename)
    df_salary = calculate_salary(df_sorted)

    # Aggregate data by name, day, and plastic type
    df_agg = df_salary.groupby(["Name", "Day", "Plastic Type"]).agg(
        {"Weight (KG)": "sum", "Salary": "sum"}
    ).reset_index()

    df_agg["Debt"] = pd.NA
    df_agg["Remaining Debt"] = pd.NA
    df_agg = input_debts(df_agg)

    # Create a payslip markdown table for each person
    payslip_tables = []
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


    # Save all the payslip tables to a text file
    with open("payslips.txt", "w") as f:
        for payslip_table in payslip_tables:
            f.write(payslip_table)
            f.write("\n")
            print(payslip_table)

if __name__ == "__main__":
    main()
