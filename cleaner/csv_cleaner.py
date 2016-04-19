import os
import re
from io import StringIO

from cleaner import utils

import pandas as pd


def strip_trailing_commas(text):
    """
    Strips unused trailing commas from the text of a csv file
    :param text: str
    :return: str
    """
    min_commas = 1000
    for n,line in enumerate(text.split("\r\n")):
        min_commas = min(min_commas, len(line) - len(line.rstrip(",")))

    if min_commas == 0:
        return text

    lines = ""
    for n, line in enumerate(text.split("\r\n")):
        lines += line[:-min_commas] + "\r\n"

    return lines


def try_to_parse_csv(local_file_path):
    """
    Applies some standardistation to the format,
    then sends the CSV text into a template for
    parsing.
    """
    with open(local_file_path, "rb") as f:
        text = f.read().decode(encoding="latin-1").strip()
        f.close()

    text = strip_trailing_commas(text)

    # count how many rows to skip
    for n, line in enumerate(text.split("\r\n")):
        if "" not in line.split(",")[-1:]:
            break

    df = pd.read_csv(StringIO(text),
                     encoding="latin-1",
                     header=n)
    cols = list(df.columns)

    # hack
    if "Name" in cols:
        df.rename(columns={"Name":"minister"}, inplace=True)
        cols = list(df.columns)
    elif "Name of Minister" in cols:
        df.rename(columns={"Name of Minister":"minister"}, inplace=True)
        cols = list(df.columns)

    minister_col = [x for x in cols if utils.like(x, ["minister"])]

    if len(minister_col) == 1:
        return try_to_parse_csv1(df)
    if len(minister_col) == 0:
        return try_to_parse_csv2(text)

    raise Exception("Too many minister columns...")


def try_to_parse_csv1(df):
    """
    Try to parse csvs, assume the standard structure and
    small variations on this theme.
    """
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

    # drop blank rows, and fill in minister's names where required
    df.dropna(how="all", inplace=True)
    if 0.05 < pd.isnull(df.minister).sum()/df.shape[0] < 1.0:
        current_minister = df.minister.values[0]
        for n, row in df.iterrows():
            if pd.isnull(row.minister):
                df.ix[n, "minister"] = current_minister
            else:
                current_minister = row.minister

    # drop final 2 rows if they contains NaNs
    if pd.isnull(df.loc[df.index[-1]]).any():
        df.drop(df.index[-1], inplace=True)

    if pd.isnull(df.loc[df.index[-1]]).any():
        df.drop(df.index[-1], inplace=True)

    return df


def try_to_parse_csv2(text):
    """
    Try to parse csvs, assume the other structure and
    small variations on this theme.
    """

    valid_substrings = [x for x in re.split(r"(,,+\r\n)(,,+\r\n)", text)
                        if len(x) > 10 and x.count("\r\n") > 1]

    valid_dfs = []
    for valid_substring in valid_substrings:

        valid_substring = strip_trailing_commas(valid_substring)

        lines = ""
        potential_ministers = []
        for line in valid_substring.split("\r\n"):
            match1 = re.match(r'(\".*(MP|Minister of|Parliamentary Under-Secretary).*\")'
                              r'|(.*(MP|Minister of|Parliamentary Under-Secretary).*,,)', line)
            if match1:
                potential_ministers.append(line[match1.start():match1.end()])
            else:
                line_values = [v for v in line.split(",") if v != ""]
                if len(line_values) == 3:
                    lines += ",".join(line_values) + "\r\n"

        assert(len(potential_ministers) == 1)
        minister = potential_ministers[0].replace('"', "").replace(",", "")

        df = pd.read_csv(StringIO(lines))
        cols = df.columns

        date_col = utils.find_column(cols, ["date", "month"])
        name_col = utils.find_column(cols, ["name of"])
        purpose_col = utils.find_column(cols, ["purpose of"])

        # fix column names
        old_cols = [date_col, name_col, purpose_col]
        new_names = ["date", "name", "purpose"]
        df = df[old_cols]
        df.rename(columns={o:n for o,n in zip(old_cols, new_names)},
                  inplace=True)
        df["minister"] = minister

        valid_dfs.append(df)

    return pd.concat(valid_dfs)
