import tkinter as tk
from enum import IntEnum
from tkinter import ttk as ttk
from tkinter.scrolledtext import ScrolledText


class EntryTypes(IntEnum):
    SINGLE_LINE = 1
    MULTI_LINE = 2


class FlatEditor(tk.Frame):
    fixed_fields = {
        "password": EntryTypes.SINGLE_LINE,
        "notes": EntryTypes.MULTI_LINE
    }

    def __init__(self, master, **kws):
        super().__init__(master, **kws)
        self.vars = {}
        self.vals = ttk.Frame(self, borderwidth=3)
        self.vals.pack(expand=1, fill=tk.BOTH)
        self.button = ttk.Button(self, text="Apply")
        self.title = None

    def get_data(self):
        ret = {}
        for k, v in self.vars.items():
            if isinstance(v, tk.Text):
                v = v.get("1.0", tk.END)
            else:
                v = v.get()

            v = v.strip()

            if v:
                ret[k] = v

        return ret

    def set_data(self, title, saved_values):
        for child in self.vals.grid_slaves():
            child.destroy()
        self.title = title
        ttk.Label(self.vals, text=title, font="bold").grid(row=0, columnspan=2, sticky="w", pady=3)
        ttk.Separator(self.vals).grid(row=1, sticky="ew", columnspan=2, pady=3)
        row = 2

        vals = {k: "" for k in self.fixed_fields}
        vals.update(saved_values)

        self.vars = {}
        for k, v in vals.items():
            style = self.fixed_fields.get(k, EntryTypes.SINGLE_LINE)

            proper = k[0].upper() + k[1:] + " :"
            ttk.Label(self.vals, text=proper).grid(row=row, sticky="nw")
            if style == EntryTypes.SINGLE_LINE:
                val = tk.StringVar()
                val.set(v)
                self.vars[k] = val
                ttk.Entry(self.vals, textvariable=val).grid(row=row, column=1, sticky="nwe")
            else:
                text = ScrolledText(self.vals, height=0, width=0)
                if v:
                    text.insert(tk.END, v)
                self.vars[k] = text
                text.grid(row=row, column=1, sticky="nsew")

                self.vals.grid_rowconfigure(row, weight=1)
                self.vals.grid_columnconfigure(1, weight=1)

            row += 1