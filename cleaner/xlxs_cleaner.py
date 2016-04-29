from cleaner import utils, csv_cleaner
import pandas as pd


def try_parse_xlsx(file_name):
    df = pd.read_excel(file_name, "Meetings")

    csv_cleaner.fix_column_names(df)

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

    # fill in blanks
    csv_cleaner.fill_in_blanks(df)

    return df
