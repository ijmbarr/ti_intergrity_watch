from __future__ import division
from cleaner import utils, csv_cleaner, odt_cleaner, xlxs_cleaner, doc_cleaner, ods_cleaner,pdf_cleaner
import os


def parse_row(row, download_to="../data/raw/"):
    """
    Main entry point for each row of the table.

    Splits, downloads, parses the documents.
    """

    row_template = utils.get_row_template(row)

    url = row_template["link"]
    link_format = url.split(".")[-1].lower()
    file_name = url.split("/")[-1]
    local_file_path = download_to + file_name

    if not os.path.exists(local_file_path):
        utils.download_file(url, local_file_path)

    if link_format == "csv":
        table_df = csv_cleaner.try_to_parse_csv(local_file_path)
    elif link_format == "pdf":
        table_df = pdf_cleaner.try_parse_pdf(local_file_path)
    elif link_format == "odt":
        table_df = odt_cleaner.try_parse_odt(local_file_path)
    elif link_format == "doc":
        table_df = doc_cleaner.try_parse_doc(local_file_path)
    elif link_format == "xlsx":
        table_df = xlxs_cleaner.try_parse_xlsx(local_file_path)
    elif link_format == "ods":
        table_df = ods_cleaner.try_parse_ods(local_file_path)
    else:
        raise Exception("Not sure how to parse {}...".format(local_file_path))

    if table_df is None:
        return None

    table_df["department"] = row_template["department"]
    table_df["period"] = row_template["period"]
    table_df["link"] = row_template["link"]

    return table_df
