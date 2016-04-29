from __future__ import division
from cleaner import csv_cleaner
import zipfile
import bs4
import pandas as pd


def try_parse_odt(file_name):
    """
    Tried to parse tables in odt files.

    Warning: if parsing fails, it will not return an error, rather it will just not return the content of that table.

    :param file_name: str
    :return: Pandas Dataframe
    """
    zf = zipfile.ZipFile(file_name)

    bs = bs4.BeautifulSoup(zf.read("content.xml"), 'xml')

    tables = bs.findAll("table")

    csv_tables = [table_to_csv(tables_to_lists(table)) for table in tables]

    success = []
    for n, table in enumerate(csv_tables):
        try:
            success.append(csv_cleaner.try_to_parse_csv(raw_text=table))
        except:
            pass

    return pd.concat(success)


def tables_to_lists(table):
    return [[tc.get_text() for tc in tr.findAll("table-cell")]
            for tr in table.findAll("table-row")]


def format_for_csv(s):
    if "," in s:
        return '"' + s + '"'
    return s


def table_to_csv(table_lst):
    return "\r\n".join([",".join([format_for_csv(y) for y in x]) for x in table_lst])
