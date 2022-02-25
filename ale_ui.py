import tkinter as tk


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        pass


class DuplicatePanel(tk.Frame):

    def __init__(self, parent, text):

        super().__init__()

        self.config(padx=5)
        self.config(pady=5)
        self.config(borderwidth=2)

        self.label_name = tk.Label(self, text="Duplicate")
        self.label_name.grid(column=0, row=0, sticky="W")

        self.label_col = tk.Label(self, text="Column")
        self.label_col.grid(column=0, row=1, sticky="W")
        self.ent_col = tk.Entry(self)
        self.ent_col.grid(column=0, row=2, sticky="W")

        self.config(width=500)
        self.config(height=84)
        self.grid_propagate(False)


if __name__ == '__main__':

    app = App()

    for i in range(10):
        rule = DuplicatePanel(app, "Duplicate"+str(1))
        rule.grid(column=0, row=i, padx=5, pady=5)

    app.mainloop()

