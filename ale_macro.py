import ale
import csv


def run_action(ale_obj, action: [str]):

    AleMacro([action], ale_obj)


class AleMacro:

    def __init__(self, macro, ale_obj: ale.Ale, manager=None):

        self.manager = manager
        self.ale_obj = ale_obj
        self.action_list = compile_macro_list(macro)
        self.execute_actions()

    def log(self, message):

        if self.manager:
            self.manager.log(message)

    def execute_actions(self):

        """execute actions in list"""

        for action in self.action_list:

            if action[0] == 'RENAME':
                self.rename(action)

            elif action[0] == 'DELETE':
                self.delete(action)

            elif action[0] == 'REMATCH':
                self.re_match(action)

            elif action[0] == 'RESUB':
                self.re_sub(action)

            elif action[0] == 'SET':
                self.set(action)

            elif action[0] == 'INCLUDE':
                self.include(action)

            else:
                raise AleMacroException(f'{action[0]}: unrecognized macro action')

    def verify_macro_action(self, action: list, length: int):

        """test that the action is valid"""

        if len(action) != length:
            raise AleMacroException(f'{action} is not a valid action')

        if action[1] not in self.ale_obj.dataframe.columns:
            raise AleMacroException(f'{action} - {action[1]} is not in the dataframe')

    def rename(self, macro):

        self.verify_macro_action(macro, 3)
        self.ale_obj.rename_column(macro[1], macro[2])

    def delete(self, macro):

        self.verify_macro_action(macro, 2)
        del (self.ale_obj.dataframe[macro[1]])

    def re_match(self, macro):

        self.verify_macro_action(macro, 3)
        self.ale_obj.regex_column(macro[1], macro[2])

    def re_sub(self, macro):

        self.verify_macro_action(macro, 4)
        self.ale_obj.regex_column(macro[1], macro[2], mode='replace', replace=macro[3])

    def set(self, macro):

        self.ale_obj.set_column(macro[1], macro[2])

    def include(self, macro):

        if len(macro) < 2:
            raise AleMacroException(f'{macro} is not a valid action')

        include = []
        missing = []

        for column in macro[1:]:

            if column in self.ale_obj.dataframe.columns:
                include.append(column)
            else:
                missing.append(column)

        self.ale_obj.dataframe = self.ale_obj.dataframe[include]

        if missing:
            self.log("The following INCLUDE columns are missing:\n" + "\n".join(missing))


class AleMacroException(Exception):
    def __init__(self, message="ALE Macro error"):
        super().__init__(message)
        self.message = message


def list_from_file(macro_file):
    """returns a list of lists based on a CSV file"""

    with open(macro_file, "r") as file_handler:
        action_list = []

        reader = csv.reader(file_handler)

        next(reader)

        for line in reader:
            this_action = [x for x in line]
            action_list.append(this_action)

    return action_list


def compile_macro_list(macro):
    if isinstance(macro, str):
        return list_from_file(macro)

    elif isinstance(macro, list):
        return macro


if __name__ == '__main__':
    test_ale = ale.Ale('AVID.ALE')
    AleMacro('presets/None.csv', test_ale)
