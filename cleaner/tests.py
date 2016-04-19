import pandas as pd
from pandas.util.testing import assert_frame_equal
from cleaner import csv_cleaner

files_to_test_csv = [
    "PM_meetings_apr_jun_14.csv",  # 0
    "141218_-_disclosure-ministerial-_meetings_Apr-Jun_14.csv",  # 10
    "Copy_of_April_to_June__2014_-__Ministeral_Meetings.csv"  # 4

]

raw_data_path = "../data/raw/"
test_data_path = "../data/test/"


def test_csvs():
    for f in files_to_test_csv:
        known = pd.read_csv(test_data_path + f, encoding="latin-1", index_col=0)
        cleaned = csv_cleaner.try_to_parse_csv(raw_data_path + f)
        assert_frame_equal(known, cleaned)
        print("CSV Test for {} Passed".format(f))
    print("All CSV passed.")


def test_all():
    test_csvs()
    print("All Passed.")
