import ale
import csv


class AleMacro:

    def __init__(self, macro_file, ale_obj: ale.Ale):

        self.ale_obj = ale_obj
        self.macro_list = list_from_file(macro_file)
        self.execute_actions()

    def execute_actions(self):

        for macro in self.macro_list:

            if macro[0] == 'RENAME':
                self.rename(macro)

            elif macro[0] == 'DELETE':
                self.delete(macro)

            elif macro[0] == 'REMATCH':
                self.re_match(macro)

            elif macro[0] == 'RESUB':
                self.re_sub(macro)

            elif macro[0] == 'SET':
                self.set(macro)

            elif macro[0] == 'INCLUDE':
                self.include(macro)

            else:
                raise ValueError(f'{macro[0]}: unrecognized macro action')

    def verify_macro(self, macro: list, length: int):

        if len(macro) != length:
            raise AleMacroException(f'{macro} is not a valid action')

        if macro[1] not in self.ale_obj.dataframe.columns:
            raise AleMacroException(f'{macro} - {macro[1]} is not in the dataframe')

    def rename(self, macro):

        self.verify_macro(macro, 3)
        self.ale_obj.rename_column(macro[1], macro[2])

    def delete(self, macro):

        self.verify_macro(macro, 2)
        del (self.ale_obj.dataframe[macro[1]])

    def re_match(self, macro):

        self.verify_macro(macro, 3)
        self.ale_obj.regex_column(macro[1], macro[2])

    def re_sub(self, macro):

        self.verify_macro(macro, 4)
        self.ale_obj.regex_column(macro[1], macro[2], mode='replace', replace=macro[3])

    def set(self, macro):

        self.ale_obj.set_column(macro[1], macro[2])

    def include(self, macro):

        if len(macro) < 2:
            raise AleMacroException(f'{macro} is not a valid action')

        columns = macro[1:]

        for column in columns:

            if column not in self.ale_obj.dataframe.columns:
                print(f'{column} could not be included. Missing in original')
                columns.remove(column)

        self.ale_obj.dataframe = self.ale_obj.dataframe[columns]


class AleMacroException(Exception):
    def __init__(self, message="ALE Macro error"):
        super().__init__(message)
        self.message = message


def list_from_file(macro_file):
    with open(macro_file, "r") as file_handler:
        macro_list = []

        reader = csv.reader(file_handler)

        next(reader)

        for line in reader:
            this_macro = [x for x in line]
            macro_list.append(this_macro)

    return macro_list


if __name__ == '__main__':
    test_ale = ale.Ale('AVID.ALE')
    AleMacro('presets/No Macro.csv', test_ale)
