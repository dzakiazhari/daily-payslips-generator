# Daily Workers Payslips Generator

Depending on the data entered, this programme generates payslips for daily workers and calculates waste picker salaries depending on the weight and kind of plastic collected.

## Daily Worker Payslip Generator

### Dependencies

The input_determined.py script requires the following Python packages:

- csv
- datetime
- typing
- pathlib
- pandas

You can install them using pip:

```
pip install pandas
```

### Usage

To use the aio_prompts.py script, simply run it in your command line interface:

```
python aio_prompts.py
```

### How to Use

1. Run the program aio_prompts.py in the command line.

2. Input the worker's name, day, plastic type, and weight (in KG) when prompted. Input "N" when you are finished inputting data for the day.

3. You will then be prompted with a few choices:

	- D - delete the last row of data 
	- L - view the current data 
	- S - save the current data and exit 
	- C - continue inputting data from the last saved data Input the price for each plastic type when prompted.

4. Input the number of workers with remaining debts.

5. Press arrow key up for prompt history.

6. Input the name, debt, and remaining debt for each worker with remaining debts.

7. The program will generate a markdown table for each worker's payslip.


### Files

- aio_prompts.py: The main program file that generates payslips for daily workers based on the data inputted.
- input_determined.py: Secondary program that has predetermined price.
- read_regenerate.py: Edit your csv and generate the revised payslips.
- timbangan_{date}.csv: The file where the data for each day is stored. The date in the filename is the date when the data was inputted.
- payment_{date}.csv: The file where the debt information for each day is stored. The date in the filename is the date when the debt information was inputted.
- price_list_{date}.txt: The file where the price list for each plastic type is stored. The date in the filename is the date when the prices were inputted.

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

This function reads two CSV files, one containing data on plastic recycling weights and the other containing individual debt information. The code manipulates and merges dataframes with pandas and generates payslips for each individual. The payslips are saved in a new text file called "revisi_payslips.txt".

The code imports three methods named "input" from another file: read_and_sort_csv, calculate_salary, and get_plastic_price. The first programme reads a CSV file containing recycling weights, sorts the data by date and time, and removes any duplicates. The second function computes each individual's income based on the amount of plastic recycled and current plastic pricing. The third function returns the current price of plastic.

Three extra functions are defined in the code:

1. read_debts: Reads in the CSV file containing debt information and returns a dataframe with the debt information indexed by individual name.
2. merge_debts: Merges the debt information with the payslip dataframe, adding columns for debt and remaining debt.
3. generate_payslips: Generates payslips for each individual and saves them to a text file.

The code's main role is to read in the two CSV files, compute each individual's income, integrate the salary and debt information, generate payslips, and save them to a new text file.
