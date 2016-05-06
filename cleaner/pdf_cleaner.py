from cleaner import csv_cleaner, utils
import PDFFixup
import pandas as pd


def try_parse_pdf(file_path):
    fixed = PDFFixup.fixer.get_tables(file_path)

    csv_tables = pdf_table_to_csvs(stitch_together_tables(fixed))

    success = []
    for n, table in enumerate(csv_tables):
        try:
            success.append(csv_cleaner.try_to_parse_csv(raw_text=table))
        except:
            pass

    return pd.concat(success)


def stitch_together_tables(tables):
    main_table = []
    for page in tables:
        for n, line in enumerate(page):
            # try to join lines that run over table breaks
            if (n == 0 and
                        len(line) >= 3 and
                        line[0] == "" and
                        len(main_table) > 0):
                for i in range(min(len(main_table[-1]), len(line))):
                    main_table[-1][i] += line[i]
            else:
                main_table.append(line)
    return main_table


def pdf_table_to_csvs(table):
    csvs = []
    s = ""
    for line in table:
        if len(line) == 1:
            csvs.append(s)
            s = ""
            s += line[0] + "\r\n"
        else:
            s += ",".join(utils.format_for_csv(c) for c in line) + "\r\n"
    csvs.append(s)
    return csvs
