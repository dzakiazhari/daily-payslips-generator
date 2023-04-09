import csv
import datetime
from typing import List
from pathlib import Path
import pandas as pd

# Reuse functions from the original input code
from input import read_and_sort_csv, calculate_salary

def read_debts(filename: str) -> pd.DataFrame:
    debts = pd.read_csv(filename, names=["Name", "Debt", "Remaining Debt"])
    return debts.set_index("Name")

def merge_debts(df: pd.DataFrame, debts: pd.DataFrame) -> pd.DataFrame:
    df["Debt"] = df["Name"].apply(lambda x: debts.loc[x, "Debt"] if x in debts.index else 0)
    df["Remaining Debt"] = df["Name"].apply(lambda x: debts.loc[x, "Remaining Debt"] if x in debts.index else 0)
    return df

def generate_payslips(df_agg: pd.DataFrame) -> str:
    payslip_tables = []
    for name in df_agg["Name"].unique():
        payslip = df_agg.loc[df_agg["Name"] == name]
        total_payment = payslip["Salary"].sum()
        total_compensation = payslip.groupby(["Plastic Type"])["Salary"].sum()
        total_weight = payslip.groupby(["Plastic Type"])["Weight (KG)"].sum()
        debt = payslip.iloc[0]["Debt"]
        remaining_debt = payslip.iloc[0]["Remaining Debt"]
        
        # Initialize last_payment with default value total_payment
        last_payment = total_payment - int(debt) if isinstance(debt, str) and debt.isdigit() else total_payment

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
        payslip_table += f"\nGaji: Rp {total_payment}"
        payslip_table += f"\nBON: Rp {debt}"
        payslip_table += f"\nSisa BON: Rp {remaining_debt}"
        payslip_table += f"\nGaji akhir: Rp {last_payment}"
        payslip_table += f"\n======***======"
        payslip_tables.append(payslip_table)

    # Save all the payslip tables to a new text file "revisi_payslips.txt"
    with open("revisi_payslips.txt", "w") as f:
        for payslip_table in payslip_tables:
            f.write(payslip_table)
            f.write("\n")
            print(payslip_table)

def main():
    today = datetime.date.today()
    timbangan_filename = f"timbangan_{today}.csv"
    payment_filename = f"payment_{today}.csv"

    df_sorted = read_and_sort_csv(timbangan_filename)
    df_salary = calculate_salary(df_sorted)
    df_agg = df_salary.groupby(["Name", "Day", "Plastic Type"]).agg(
        {"Weight (KG)": "sum", "Salary": "sum"}
    ).reset_index()

    debts = read_debts(payment_filename)
    df_agg = merge_debts(df_agg, debts)
    generate_payslips(df_agg)

if __name__ == "__main__":
    main()
