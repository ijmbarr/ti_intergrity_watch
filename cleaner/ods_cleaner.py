import ezodf
from cleaner import csv_cleaner, utils


def try_parse_ods(file_path):
    doc = ezodf.opendoc(file_path)

    csved = convert_odf_to_csv(get_sheet(doc.sheets))

    df = csv_cleaner.try_to_parse_csv(raw_text=csved)

    return df


def format_for_csv(s):
    if s is None:
        return ""
    if "," in s:
        return '"' + s + '"'
    return s


def convert_odf_to_csv(sheet):
    ss = []
    for row in sheet.rows():
        ss.append(",".join([format_for_csv(cell.value) for cell in row]))

    return "\r\n".join(ss)


def get_sheet(sheets):
    possible = [sheet for sheet in sheets
                if "meetings" in utils.normalise(sheet.name)]
    assert(len(possible) == 1)
    return possible[0]
