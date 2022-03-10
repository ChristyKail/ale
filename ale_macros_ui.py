import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import ale
import ale_macro


class AleMacrosApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.preset_folder, self.macro_list = get_macros()

        self.setup_ui()

        self.loaded_ale = None

    # noinspection PyAttributeOutsideInit
    def setup_ui(self):

        self.title("Cinelab Film & Digital - ALE Macros")

        try:
            self.logo_image = tk.PhotoImage(file="CFD-Icon_Standard.png")
            self.tk.call('wm', 'iconphoto', self._w, tk.PhotoImage(file="CFD-Icon_Standard.png"))

        except Exception as exception:
            print("Logo failed to load. Reason:", exception)

        else:
            self.label_logo = tk.Label(self, image=self.logo_image, pady=10)
            self.label_logo.grid(column=0, row=0, columnspan=4, sticky="EW")

        # noinspection PyTypeChecker
        self.columnconfigure(tuple(range(4)), weight=1, minsize=5, pad=10)
        # noinspection PyTypeChecker
        self.rowconfigure(tuple(range(8)), weight=1, pad=5)

        # macro selector
        self.combo_macro = ttk.Combobox(self, values=self.macro_list, width=20, state="readonly")
        self.combo_macro.set("None")
        self.combo_macro.grid(column=1, row=1, columnspan=2, sticky="EW")

        btn_width = 10

        # run
        self.btn_run = tk.Button(self, text="Run", command=self.single_run, width=btn_width)
        self.btn_run.grid(column=0, row=2, padx=5, pady=5)

        # batch run
        self.btn_batch_run = tk.Button(self, text="Batch run", command=self.batch_run, width=btn_width)
        self.btn_batch_run.grid(column=1, row=2, padx=5, pady=5)

        # batch run
        self.btn_batch_append = tk.Button(self, text="Batch append", command=self.batch_append, width=btn_width)
        self.btn_batch_append.grid(column=2, row=2, padx=5, pady=5)

        # SS DR merge
        self.btn_ss_dr_merge = tk.Button(self, text="SS DR merge", command=self.ss_dr_merge, width=btn_width)
        self.btn_ss_dr_merge.grid(column=3, row=2, padx=5, pady=5)

        # preview
        self.text_preview = tk.Text(self, width=75, takefocus=0, highlightthickness=0, padx=5, pady=5,
                                    wrap='none')
        self.text_preview.grid(column=0, row=3, columnspan=4, sticky="NEW", pady=10, padx=10)
        self.text_preview['state'] = 'disabled'

        # ALE out
        self.btn_ale_out = tk.Button(self, text="Save ALE", command=self.ale_out, width=btn_width)
        self.btn_ale_out.grid(column=1, row=4, padx=5, pady=5)

        # CSV out
        self.btn_csv_out = tk.Button(self, text="Save CSV", command=self.csv_out, width=btn_width)
        self.btn_csv_out.grid(column=2, row=4, padx=5, pady=5)

    def get_current_macro(self):

        preset_name = self.combo_macro.get()

        return os.path.join(self.preset_folder, f'{preset_name}.csv')

    def run_current(self):

        try:
            ale_macro.AleMacro(self.get_current_macro(), self.loaded_ale, manager=self)
        except ale_macro.AleMacroException as exception:
            messagebox.showerror('AleMacroException', message=exception.message)
        except ale.AleException as exception:
            messagebox.showerror('AleException', message=exception.message)
        else:
            self.update_preview()

    def single_run(self):

        ale_filename = filedialog.askopenfilename(filetypes=[('ALE files', '*.ale *.ALE')])

        if not ale_filename:
            return

        self.loaded_ale = ale.Ale(ale_filename)
        self.run_current()

    def batch_run(self):

        ale_filenames = filedialog.askopenfilenames(filetypes=[('ALE files', '*.ale *.ALE')])

        if not ale_filenames:
            return

        for ale_filename in ale_filenames:
            self.loaded_ale = ale.Ale(ale_filename)
            self.run_current()
            self.loaded_ale.to_file(self.loaded_ale.filename.replace('.ale', ' - batch processed.ale'))

    def batch_append(self):
        raise NotImplementedError()

    def ss_dr_merge(self):

        folder_name = filedialog.askdirectory()

        if not folder_name:
            return

        dr_folder = os.path.join(folder_name, 'DR')
        ss_folder = os.path.join(folder_name, 'SS')

        try:
            dr_ale_obj = ale.append_multiple(ale.load_folder(dr_folder))
            ss_ale_obj = ale.append_multiple(ale.load_folder(ss_folder))

        except FileNotFoundError:
            messagebox.showerror('Error', message="No valid folder structure found. ALEs should be placed in their "
                                                  "respective SS and DR folders")
            return

        errors = dr_ale_obj.merge(ss_ale_obj, return_errors=True)

        if len(errors[1]) or len(errors[2]):
            self.log('The following clips have no matches:\n'+'\n'.join(errors[1])+'\n'.join(errors[2]))

        self.loaded_ale = dr_ale_obj.merge(ss_ale_obj)

        self.run_current()

    def ale_out(self):

        if not self.loaded_ale:
            messagebox.showerror('Error', 'No ALE loaded to export')

        out_filename = filedialog.asksaveasfilename()

        if not out_filename:
            return

        self.loaded_ale.to_file(out_filename)

    def csv_out(self):

        if not self.loaded_ale:
            messagebox.showerror('Error', 'No ALE loaded to export')

        out_filename = filedialog.asksaveasfilename()

        if not out_filename:
            return

        self.loaded_ale.to_csv(out_filename)

    def update_preview(self):

        self.text_preview['state'] = 'normal'
        self.text_preview.delete(0.0, 'end')
        self.text_preview.insert(0.0, str(self.loaded_ale))
        print(self.loaded_ale.dataframe.to_string(index=False))
        self.text_preview['state'] = 'disabled'
        self.update()

    def log(self, message):
        messagebox.showinfo("ALE Macro Log", message)


def get_macros():
    macro_list = []

    preset_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'presets')

    for file in os.listdir(preset_folder):

        if file.endswith('.csv'):
            macro_list.append(file.replace('.csv', ''))

    macro_list.sort()

    return preset_folder, macro_list


if __name__ == '__main__':
    app = AleMacrosApp()
    app.mainloop()
