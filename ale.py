import re

import columns as columns
import pandas
import os
import csv


class Ale:

    def __init__(self, filename: str = None):

        self.name = "Empty"
        self.filename = ""

        self.heading = {}

        self.dataframe = pandas.DataFrame()

        if filename:
            self.load_from_file(filename)

    def __repr__(self):

        to_return = str()

        for index, value in self.heading.items():
            to_return = to_return + f'{index}\t{value}\n'

        to_return = to_return + "\n"

        to_return = to_return + self.dataframe.to_string()

        return to_return

    def load_from_file(self, filename):

        """load an ALE file into the ALE object"""

        if not os.path.isfile(filename):
            raise FileNotFoundError(f'{filename} is not a valid file')

        self.name = os.path.basename(filename)
        self.filename = filename

        skip_rows = []

        index_priority = ["Name", "Labroll", "Tape", "Start"]

        with open(filename, "r") as file_handler:

            for line_index, line_content in enumerate(file_handler):

                if line_content.strip() == "Column":
                    skip_rows = list(range(0, line_index + 1))
                    skip_rows.append(line_index + 2)
                    skip_rows.append(line_index + 3)

                    break

                if line_content.strip() == "Heading":

                    pass

                elif line_content.strip() == "":

                    pass

                else:

                    add_to_heading = line_content.strip().split(maxsplit=1)

                    self.heading[add_to_heading[0]] = add_to_heading[1]

        self.dataframe = pandas.read_csv(filename, sep="\t", skiprows=skip_rows, dtype=str, engine="python",
                                         keep_default_na=False, index_col=0)

        # for value in index_priority:
        #     if value in self.dataframe:
        #         self.dataframe.set_index(value, inplace=True)
        #         break

        self.dataframe = self.dataframe.loc[:, ~self.dataframe.columns.str.contains('^Unnamed')]

    def append(self, other, inplace=False, return_errors=False):

        """add an ALE to this one by row"""

        merged_ale = Ale()

        if self.dataframe.empty:
            merged_ale = other.dataframe.copy()

        else:
            merged_ale.dataframe = pandas.concat([self.dataframe, other.dataframe], axis=0, ignore_index=True)

        if inplace:
            self.dataframe = merged_ale.dataframe

        if return_errors:
            cols_self = set(self.dataframe.columns)
            cols_other = set(other.dataframe.columns)

            missing_from_self = cols_other - cols_self
            missing_from_other = cols_self - cols_other

            # Return number of missing, list of missing from self, list of missing from other
            return (len(missing_from_self) + len(missing_from_other)), missing_from_self, missing_from_other

        return merged_ale

    def merge(self, other, match_on=None, inplace=False, return_errors=False):

        """add an ALE to this one by column"""

        if match_on is None:
            match_on = ["Tape", "Start"]

        merged_ale = Ale()

        if self.dataframe.empty:
            merged_ale.dataframe = other.dataframe.copy()

        else:
            merged_ale.dataframe = pandas.merge(self.dataframe, other.dataframe, how="outer", on=match_on,
                                                suffixes=("", "_%2"), indicator="%from_ale")

        if inplace:
            self.dataframe = merged_ale.dataframe

        if return_errors:

            # check for rows that only exist in one dataframe

            diff_df = merged_ale.dataframe.loc[merged_ale.dataframe['%from_ale'] != 'both'].copy()

            diff_df["Match"] = ""
            diff_df.reset_index(inplace=True)

            for col in match_on:
                diff_df["Match"] = diff_df["Match"] + " " + diff_df[col]

            left_only = [value for index, value in enumerate(diff_df["Match"]) if
                         diff_df["%from_ale"][index] == "left_only"]
            right_only = [value for index, value in enumerate(diff_df["Match"]) if
                          diff_df["%from_ale"][index] == "right_only"]

            # check for columns that are duplicated

            duplicate_columns = [value.strip("_%2") for value in diff_df.columns if "_%2" in value]

            # Return number of mismatches,  list of items in self with no match, list of items in other with no match,
            # list of duplicates
            return len(diff_df), left_only, right_only, duplicate_columns

        merged_ale.heading = self.heading

        merged_ale.dataframe.drop(['%from_ale'], axis=1)

        return merged_ale

    def validate(self):

        """check if this ALE is likely to cause any issues"""

        working = self.dataframe.copy()

        # check for duplicates
        columns = [col.lower() for col in working.columns]
        seen = set()
        dupes = [x for x in columns if x in seen or seen.add(x)]
        print(dupes)

        pass

    def to_csv(self, filename):

        """save ALE data to CSV file on disk"""

        self.dataframe.to_csv(filename, sep='\t', index=False, header=True, quoting=csv.QUOTE_NONE,
                              columns=list(self.dataframe))

    def to_file(self, filename):

        """save out ALE object to ALE file on disk"""

        self.dataframe.to_csv(filename, sep='\t', index=False, header=True, quoting=csv.QUOTE_NONE,
                              columns=list(self.dataframe))

        data_as_lines = []

        with open(filename, 'r+') as file_handler:
            for line_contents in file_handler:
                data_as_lines.append(line_contents.strip("\n"))

        file_output = ['Heading']

        for key, value in self.heading.items():
            file_output.append(f'{key}\t{value}')

        file_output.append("")

        file_output.append("Column")

        file_output.append(data_as_lines[0])

        file_output.append("\nData")

        file_output = file_output + data_as_lines[1:]

        with open(filename, 'w') as file_handler:
            file_handler.seek(0, 0)
            file_handler.write("\n".join(file_output))

        return "\n".join(file_output)

    def sort_columns(self, ):

        cols_order = sorted(self.dataframe.columns.to_list())
        self.dataframe = self.dataframe[cols_order]

        return self.dataframe

    def sort_rows(self, sort_by_columns: []):

        self.dataframe = self.dataframe.sort_index(sort_by_columns)

    def duplicate_col(self, source_column, destination_column, overwrite=True):

        if source_column not in self.dataframe.columns:
            raise ValueError(f'{source_column} not in ALE')

        if destination_column not in self.dataframe.columns or overwrite:
            self.dataframe[destination_column] = self.dataframe[source_column]

        else:
            raise ValueError(f'{destination_column} already in ALE, use overwrite option to set anyway')

    def rename_column(self, column, new_name):

        self.dataframe.rename(columns={column: new_name}, inplace=True)

    def set_column(self, column, value):

        self.dataframe[column] = value

        dynamic_matches = re.findall(r'{[a-zA-Z0-9 _-]+}', value)

        for match_tag in dynamic_matches:

            match_string = match_tag.strip("{").strip("}")

            if match_string not in self.dataframe.columns:

                print(self.dataframe.columns)
                raise ValueError(f"{match_string} isn't in the dataframe")

            else:
                for index, value in enumerate(self.dataframe[column]):
                    self.dataframe[column][index] = value.replace(match_tag, self.dataframe[match_string][index])

    def regex_column(self, column, regex, mode="replace", replace=""):

        for index, original_value in enumerate(self.dataframe[column]):

            new_value = "new_value"

            if mode == "replace":
                new_value = re.sub(regex, replace, original_value)
                print("replace", original_value, replace)

            elif mode == "match":

                matches = re.findall(regex, original_value)
                new_value = "".join(matches)

            self.dataframe[column][index] = new_value


if __name__ == '__main__':
    # NOT PART OF THE MODULE, FOR TESTING ONLY

    ale1 = Ale("Mini Raw all.ale")

    ale2 = Ale("Mini Raw missing .ale")

    ale1.set_column("Aardvark", "{Shutter}")

    ale1.regex_column("Aardvark", r"0+$")
    ale1.regex_column("Aardvark", r"(?<=^\d{3})", replace=".")


    print(ale1.sort_columns())

    print(r"(?=\d\d$)")
