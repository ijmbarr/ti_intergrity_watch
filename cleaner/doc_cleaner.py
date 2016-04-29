import os
import bs4
from cleaner import csv_cleaner
import pandas as pd

HTML_PATH = "../data/htmled/"


def try_parse_doc(file_path):

    file_name = os.path.split(file_path)[-1]
    htmled = HTML_PATH + file_name + ".html"

    if not os.path.exists(htmled):
        convert_to_html(file_path)

    with open(htmled, "rb") as f:
        text = f.read()
        f.close()

    bs = bs4.BeautifulSoup(text, 'html.parser')

    tables = bs.findAll("table")

    csv_tables = [table_to_csv(tables_to_lists(table)) for table in tables]

    success = []
    for n, table in enumerate(csv_tables):
        try:
            success.append(csv_cleaner.try_to_parse_csv(raw_text=table))
        except:
            pass

    return pd.concat(success)


def convert_to_html(file_path):
    raise Exception("convert_to_html not implemented yet")


def tables_to_lists(table):
    return [[td.get_text() for td in tr.findAll("td")]
             for tr in table.findAll("tr")]


def format_for_csv(s):
    if "," in s:
        return '"' + s + '"'
    return s


def table_to_csv(table_lst):
    return "\r\n".join([",".join([format_for_csv(y) for y in x]) for x in table_lst])
