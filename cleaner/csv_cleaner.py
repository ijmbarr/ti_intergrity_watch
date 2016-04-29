from __future__ import division
import os
import re
from StringIO import StringIO

from CSVFixup import CSVFixup
from cleaner import utils
import pandas as pd


def strip_trailing_commas(text):
    """
    Strips unused trailing commas from the text of a csv file
    :param text: str
    :return: str
    """
    min_commas = 1000
    for n, line in enumerate(text.split("\r\n")):
        min_commas = min(min_commas, len(line) - len(line.rstrip(",")))

    if min_commas == 0:
        return text

    lines = ""
    for n, line in enumerate(text.split("\r\n")):
        lines += line[:-min_commas] + "\r\n"

    return lines


def try_to_parse_csv(*args, **kargs):
    """
    Applies some standardistation to the format,
    then sends the CSV text into a template for
    parsing.
    """
    fcsv = CSVFixup(*args, **kargs)

    inferred_structure = infer_structure(fcsv.tables)

    if inferred_structure == 1:
        return try_to_parse_csv1(fcsv.tables)
    elif inferred_structure == 2:
        return try_to_parse_csv2(fcsv.tables)

    raise Exception("Not sure how to parse this table.")


def fix_column_names(df):
    df.rename(columns={
        "Name": "minister",
        "Name of Minister": "minister"
    }, inplace=True)


def infer_structure(tables):
    for t in tables:
        if not (len(t.fixed_table[0]) == 1):
            attempt = pd.read_csv(StringIO(t.fixed_table_text()))
            if attempt.columns.shape[0] == 4:
                return 1
            elif attempt.columns.shape[0] == 3:
                return 2
    return -1


def try_to_parse_csv1(tables):
    """
    Try to parse csvs, assume the standard structure and
    small variations on this theme.
    """
    past_column_names = None
    cleaned_tables = []
    for table in tables:
        if not (len(table.fixed_table[0]) == 1):
            df = pd.read_csv(StringIO(table.fixed_table_text()))
            fix_column_names(df)

            cols = list(df.columns)

            minister_col = utils.find_column(cols, ["minister"])
            date_col = utils.find_column(cols, ["date", "month"])
            name_col = utils.find_column(cols, ["name of"])
            purpose_col = utils.find_column(cols, ["purpose of"])

            # fix column names
            old_cols = [minister_col, date_col, name_col, purpose_col]
            new_names = ["minister", "date", "name", "purpose"]
            df = df[old_cols]
            df.rename(columns={o: n for o, n in zip(old_cols, new_names)},
                      inplace=True)

            # drop final 2 rows if they contains NaNs
            if pd.isnull(df.loc[df.index[-1]][["name"]]).any():
                df.drop(df.index[-1], inplace=True)

            if pd.isnull(df.loc[df.index[-1]][["name"]]).any():
                df.drop(df.index[-1], inplace=True)

            fill_in_blanks(df)

            cleaned_tables.append(df)

    return pd.concat(cleaned_tables)


def try_to_parse_csv2(tables):
    """
    Try to parse csvs, assume the other structure and
    small variations on this theme.
    """

    cleaned_tables = []
    for table in tables:
        if not (len(table.fixed_table[0]) == 1):
            df = pd.read_csv(StringIO(table.fixed_table_text()))
            fix_column_names(df)

            cols = list(df.columns)

            date_col = utils.find_column(cols, ["date", "month"])
            name_col = utils.find_column(cols, ["name of"])
            purpose_col = utils.find_column(cols, ["purpose of"])

            # fix column names
            old_cols = [date_col, name_col, purpose_col]
            new_names = ["date", "name", "purpose"]
            df = df[old_cols]
            df.rename(columns={o: n for o, n in zip(old_cols, new_names)},
                      inplace=True)

            df["minister"] = get_minister(table.meta_data)

            fill_in_blanks(df)

            cleaned_tables.append(df)

    return pd.concat(cleaned_tables)


def get_minister(lst):
    minister_pattern1 = r'.*MP.*'

    minister_guess = [e for e in lst
                      if re.match(minister_pattern1, e)]

    if len(minister_guess) == 1:
        return minister_guess[0]


    minister_pattern2 = (r'(\".*(Minister of|Parliamentary Under-Secretary|Secretary of|Minister for|Home Secretary).*\")'
                        r'|(.*(Minister of|Parliamentary Under-Secretary|Secretary of|Minister for|Home Secretary).*)')
    minister_guess = [e for e in lst
                      if re.match(minister_pattern2, e)]

    assert(len(minister_guess) == 1)

    return minister_guess[0]


def fill_in_blanks(df):
    row = df.iloc[0]
    current_minister = row.minister
    current_date = row.date
    current_purpose = row.purpose

    for n, row in df.iterrows():
        if not pd.isnull(row.name):
            if pd.isnull(row.minister):
                df.ix[n, "minister"] = current_minister
            else:
                current_minister = row.minister

            if pd.isnull(row.date):
                df.ix[n, "date"] = current_date
            else:
                current_date = row.date

            if pd.isnull(row.purpose):
                df.ix[n, "purpose"] = current_purpose
            else:
                current_purpose = row.purpose
