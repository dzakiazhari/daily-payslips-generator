import os
from prettytable import PrettyTable
from datetime import datetime
from mdformat import text as mdformat_text
from tkinter import Tk
from tkinter.filedialog import askdirectory


def prettify_markdown_file(file_path, output_folder, msword_friendly, padding_width=1):
    with open(file_path, 'r') as f:
        content = f.read()

    # Find tables and format them using prettytable
    table_start = False
    table_lines = []
    formatted_content = ""
    in_numbered_list = False  # Track whether currently inside a numbered list
    list_counter = 1  # Counter for numbering the list items
    for line in content.splitlines():
        if line.strip().startswith("|"):
            if not table_start:
                table_start = True
            table_lines.append(line)
        else:
            if table_start:
                formatted_content += format_table(table_lines, msword_friendly, padding_width)
                table_lines = []
                table_start = False
            line = line.strip()
            if line.startswith(str(list_counter) + "."):
                in_numbered_list = True
                formatted_content += line + "\n"
                list_counter += 1
            elif in_numbered_list:
                in_numbered_list = False
                if line:  # Check if the line is not empty
                    formatted_content += line + "\n"
                formatted_content += "\n"
            else:
                formatted_content += line + "\n"

    formatted_content += format_table(table_lines, msword_friendly, padding_width) if table_start else ""

    # Format the remaining Markdown content
    formatted_content = formatted_content.replace("mdformat.text", "format")

    file_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(file_name)[0]
    output_file_name = (
        f"HASIL_{file_name_without_ext}_{datetime.now().strftime('%Y-%m-%d')}.md" if msword_friendly
        else f"HASIL_{file_name_without_ext}_{datetime.now().strftime('%Y-%m-%d')}_prettified.md"
    )
    output_file_path = os.path.join(output_folder, output_file_name)

    with open(output_file_path, 'w') as f:
        f.write(formatted_content)


def format_table(table_lines, msword_friendly, padding_width=1):
    if table_lines:
        headers = [cell.strip() for cell in table_lines[0].strip().split("|")[1:-1]]
        rows = [[cell.strip() for cell in line.strip().split("|")[1:-1]] for line in table_lines[2:]]
        max_column_widths = [max([len(row[i]) for row in rows] + [len(headers[i])]) for i in range(len(headers))]

        table = PrettyTable()
        table.field_names = headers

        if msword_friendly:
            table.horizontal_char = "="
            table.vertical_char = "|"
            table.junction_char = "|"
            table.header_separator_char = "="
            table.bottom_border_char = "="
            table.top_border_char = "="

        for row in rows:
            table.add_row(row)

        table.align = "l"

        formatted_table = str(table)
        formatted_table = formatted_table.replace("\n", "\n" + " " * padding_width)
        formatted_table = formatted_table.replace("|", " " * padding_width + "|" + " " * padding_width)
        formatted_table = formatted_table.replace("+", "-" * (max_column_widths[0] + 2 * padding_width))

        return formatted_table + "\n\n"
    else:
        return ""


def prettify_folder(folder_path, output_folder, msword_friendly, padding_width):
    markdown_files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and (file_name.endswith('.md') or file_name.endswith('.txt')):
            markdown_files.append(file_path)

    print("Daftar file Markdown:")
    for i, file_path in enumerate(markdown_files, start=1):
        print(f"{i}. {file_path}")

    proceed = input("\nApakah Anda yakin ingin mempercantik/merapikan tampilan file-file berikut? (Y/N): ")
    if proceed.upper() != 'Y':
        print("Operasi dibatalkan.")
        return

    for file_path in markdown_files:
        print(f"\nMempercantik tampilan file: {file_path}")
        prettify_markdown_file(file_path, output_folder, msword_friendly, padding_width)

    print("\nPempercantikan tampilan selesai. File-file yang telah dipercantik tersimpan di folder 'MARKDOWN'.")


def merge_files(input_folder, output_folder):
    merged_content = ""
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                merged_content += content + "\n\n"

    date = datetime.now().strftime('%Y-%m-%d')
    merged_file_name_md = f"HASIL_GABUNGAN_FINAL_{date}.md"
    merged_file_name_txt = f"HASIL_GABUNGAN_FINAL_{date}.txt"

    merged_file_path_md = os.path.join(output_folder, merged_file_name_md)
    merged_file_path_txt = os.path.join(output_folder, merged_file_name_txt)

    with open(merged_file_path_md, 'w') as f_md, open(merged_file_path_txt, 'w') as f_txt:
        f_md.write(merged_content)
        f_txt.write(merged_content)

    print(f"Gabungan file disimpan di:\n{merged_file_path_md}\n{merged_file_path_txt}")


def main():
    Tk().withdraw()  # Sembunyikan jendela utama
    folder_path = askdirectory(title="Pilih Folder")  # Buka dialog penjelajah file untuk memilih folder
    if folder_path:
        output_folder = os.path.join(folder_path, "MARKDOWN")
        os.makedirs(output_folder, exist_ok=True)

        print("Pilih opsi pempercantikan tampilan:")
        print("1. Pempercantikan Tampilan sederhana (Basic)")
        print("2. Pempercantikan Tampilan format MS Word")
        option = input("Masukkan pilihan Anda (1 atau 2): ")

        padding_width = int(input("Masukkan lebar jarak: "))

        if option == "1":
            prettify_folder(folder_path, output_folder, False, padding_width)
        elif option == "2":
            prettify_folder(folder_path, output_folder, True, padding_width)
        else:
            print("Opsi yang tidak valid dipilih. Operasi dibatalkan.")

        merge_prompt = input("Apakah Anda ingin menggabungkan semua file? (y/n): ")
        if merge_prompt.lower() == "y":
            merge_files(output_folder, output_folder)
    else:
        print("Tidak ada folder yang dipilih. Operasi dibatalkan.")


if __name__ == "__main__":
    main()

