# Daily Workers Payslips Generator

This programme makes pay stubs for daily workers based on the information they enter, and it figures out how much waste pickers get paid based on the weight and type of plastic they gather.

## Daily Worker Payslip Generator

### Dependencies

The scripts require the following Python packages:

- csv
- datetime
- typing
- pathlib
- pandas
- prompt-toolkit


### Usage

To use the aio_prompts.py script, simply run it in your command line interface:

```
python aio_prompts.py
```

### How to Use

1. Type aio_prompts.py into the command line and run it.

2. When asked, enter the worker's name, day, type of plastic, and weight (in KG). When you are done entering info for the day, type "N".

3. You will then be given a few options to choose from:
	- D: Delete the last row of data 
	- L: View the current data 
	- S: Save the current data and leave
	- C: keep entering info from the last time it was saved.

4. Type in the number of workers who still owe money.

5. Press the up arrow key to see the past prompt.

6. Type in the name, debt, and debt left for each person who still owes money.

7. For each worker's paycheck, the programme will make a discount table.


### Files

- aio_prompts.py: main programme file that uses the information entered to make payslips for daily workers.
- read_regenerate.py: Change your CSV file and make new payslips.
- check_input.py: Check your input based on database.xlsx
- prettify-md.py: Prettify your md files.
- timbangan_{date}.csv: The file where each day's info is kept. The date in the title is the date that the information was put into the file.
- payment_date.csv is the file where each day's debt information is kept. The date in the name of the file is the date that the information about the debt was put in.
- The file price_list_date>.txt is where the price list for each type of plastic is kept. The numbers were put in on the date shown in the filename.


## Predetermined Pricing

You will be prompted to enter the following information for each waste picker:

- Name
- Day of the week
- Type of plastic collected
- Weight of plastic collected

After entering the data for each waste picker, the script will generate a CSV file with the name timbangan_<date>.csv, where <date> is the current date. The CSV file contains the following information:

- Name
- Day of the week
- Type of plastic collected
- Weight of plastic collected

The script will then calculate the salary of each waste picker based on the data in the CSV file. The salary is calculated as follows:

- For each type of plastic collected, the script uses a price map to determine the price of that type of plastic.
- The script multiplies the weight of plastic collected by the price of that type of plastic to calculate the salary for each waste picker.
- The script will then aggregate the data by name, day, and plastic type and generate a payslip for each waste picker.

The payslip contains the following information:

- Name
- Total weight of plastic collected
- Total salary earned
- Total compensation earned for each type of plastic collected
- Debt (if any)
- Remaining debt (if any)

If a waste picker has a debt, the script will subtract the debt from the total payment to calculate the last payment.

You can also input debts and remaining debts for waste pickers. The script will prompt you to enter the following information for each waste picker with a debt:

- Name
- Debt
- Remaining debt

The script will generate a CSV file with the name payment_<date>.csv, where <date> is the current date. The CSV file contains the following

## CSV Read & Generate

This method reads two CSV files. One has information about how much plastic can be recycled, and the other has information about each person's debt. The code manipulates dataframes, joins them with pandas, and makes paystubs for each person. The pay stubs are saved in a new text file called "revisi_payslips.txt."

The code imports from another file three methods called "input": read_and_sort_csv, calculate_salary, and get_plastic_price. The first tool reads recycling weights from a CSV file, sorts them by date and time, and gets rid of any duplicates. The second function figures out how much money each person makes based on how much plastic they recover and how much plastic costs right now. The third feature gives back the price of plastic right now.

In the code, three extra methods are set up:

1. read_debts: Reads in a CSV file with information about debts and gives back a dataframe with the debt information organised by person's name.
2. merge_debts: Combines the debt information with the payslip dataframe, adding columns for debt and leftover debt.
3. generate_payslips: Creates payslips for each person and saves them to a text file.

The main job of the code is to read the two CSV files, figure out how much money each person makes, combine the salary and debt information, make payslips, and save them to a new text file.
