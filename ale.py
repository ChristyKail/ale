import pandas
import os
import csv


class Ale:

    def __init__(self, filename: str = None):

        self.name = "Empty"

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

            missing_from_self = cols_other-cols_self
            missing_from_other = cols_self-cols_other

            return (len(missing_from_self)+len(missing_from_other)), missing_from_self, missing_from_other

        return merged_ale

    def merge(self, other, match_on=["Start"], inplace=False, return_errors=True):

        """add an ALE to this one by column"""
        merged_ale = Ale()

        if self.dataframe.empty:
            merged_ale = other.dataframe.copy()

        else:
            merged_ale = pandas.merge(self.dataframe, other.dataframe, how="outer", on=match_on, suffixes=("", "_2"))

        if inplace:
            self.dataframe = merged_ale.dataframe

        # if return_errors:

        match_self = self.dataframe[match_on]
        match_other = other.dataframe[match_on]

        diff_df = pandas.merge(match_self, match_other, how='outer', indicator='Exist')
        diff_df = diff_df.loc[diff_df['Exist'] != 'both']

        print(diff_df)

        return diff_df

    def validate(self):

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


if __name__ == '__main__':
    ale1 = Ale("Bin 1.ale")

    ale2 = Ale("TEST.ALE")

    count, missing_self, missing_other = ale1.append(ale2, return_errors=True)

    print(f'{count}\nMissing in {ale1.name}: {missing_self}\nMissing in {ale2.name}: {missing_other}')
