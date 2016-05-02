from __future__ import division

class FixupLine:
    def __init__(self, line):
        self.line = line
        self.length = len(line)
        self.non_empty_count = len([l for l in line if l != ""])
        self.empty = self.non_empty_count == 0
        self.row = None


class FixupTable:
    def __init__(self, lines):
        self.lines = lines

        # assign row number
        for n, l in enumerate(lines):
            l.row = n

        self.meta_data = []
        self.fixed_table = []
        self.fix_table()

    def infer_header(self):
        # assume that the first and longest is the header.
        max_non_empty_count = max([l.non_empty_count for l in self.lines])
        for line in self.lines:
            if line.non_empty_count == max_non_empty_count:
                return line.row, max_non_empty_count

    def count_columns(self):
        row_length = max([l.length for l in self.lines])
        column_counts = [0] * row_length
        for line in self.lines:
            for n, e in enumerate(line.line):
                if e != "":
                    column_counts[n] += 1

        return column_counts

    def fix_table(self):
        fixed_table = []
        meta_data = []
        header_row, row_length = self.infer_header()

        column_counts = self.count_columns()
        data_columns = sorted(
            [x[0] for x in
             sorted(enumerate(column_counts), key=lambda x:x[1], reverse=True)]
            [:row_length])

        for line in self.lines:
            if line.row < header_row:
                meta_data.append(line)
            elif line.row == header_row:
                fixed_table.append(self.remove_empty(line.line))
            elif line.row > header_row:
                fixed_table.append([try_to_get_index(line.line, i, "") for i in data_columns])

        self.fixed_table = fixed_table
        self.meta_data = [e for l in meta_data for e in l.line
                          if e != ""]

    def fixed_table_text(self):
        return "\n".join([",".join(line) for line in self.fixed_table])

    @staticmethod
    def remove_empty(line):
        return [x for x in line if x != ""]


class CSVFixup:

    def __init__(self, file_name=None, raw_text=None):

        if file_name is not None:
            with open(file_name, "rb") as f:
                text = f.read().decode("latin-1").strip()
                f.close()
        elif raw_text is not None:
            text = raw_text
        else:
             raise Exception("Need to specify a file or raw text")

        self.raw = text

        self.line_delimiter = "\r\n"
        self.row_delimiter = ","
        self.quote_character = '"'

        lines = self.split_into_lines(text)
        lines = [self.split_line(line) for line in lines]
        self.lines = lines

        self.empty_lines_to_split_by = 2
        self.tables = []
        self.split_into_tables(lines)

    def split_into_lines(self, text):
        return text.split(self.line_delimiter)

    def split_line(self, line):
        output_list = []
        quote_open = False
        string_so_far = ""
        for c in line:
            if c == self.quote_character:
                quote_open = not quote_open
                string_so_far += c
            elif not quote_open and c == self.row_delimiter:
                output_list.append(string_so_far)
                string_so_far = ""
            else:
                string_so_far += c

        output_list.append(string_so_far)

        return FixupLine(output_list)

    def split_into_tables(self, lines):
        empty_count = 0
        current_table = []
        table_record = []

        for line in lines:
            if line.empty:
                empty_count += 1
            else:
                if empty_count > self.empty_lines_to_split_by:
                    if current_table:
                        table_record.append(current_table)
                    current_table = [line]
                else:
                    current_table.append(line)
                empty_count = 0

        if current_table:
            table_record.append(current_table)

        self.tables = [FixupTable(t) for t in table_record]


def try_to_get_index(lst, idx, default=None):
    if idx > len(lst) - 1:
        return default
    return lst[idx]