import os
import tkinter as tk
from tkinter import ttk as ttk


class HideScroll(tk.Scrollbar):
    """Create a scrollbar that hides iteself if it's not needed. Only
    works if you use the pack geometry manager from tkinter.
    """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            if self.cget("orient") == tk.HORIZONTAL:
                self.pack(fill=tk.X, side=tk.BOTTOM)
            else:
                self.pack(fill=tk.Y, side=tk.RIGHT)
        tk.Scrollbar.set(self, lo, hi)

    def grid(self, **kw):
        raise tk.TclError("cannot use grid with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")


class FileTree(tk.Frame):
    def __init__(self, master, path):
        self.current_node = None
        tk.Frame.__init__(self, master, bg="black")

        self.tree = ttk.Treeview(self, show="tree")
        ysb = HideScroll(self, orient='vertical', command=self.tree.yview)
        xsb = HideScroll(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        abspath = os.path.abspath(path)
        root = self.tree.insert('', 'end', text="Passwords", open=True, tag='r')
        self.process_directory(root, abspath)

        self.tree.pack(expand=1, fill=tk.BOTH)
        self.tree.tag_bind('f', '<<TreeviewSelect>>', self.open_node)

    def open_node(self, _event):
        self.current_node = self.tree.selection()
        abspath = self.tree.item(self.current_node).get("values")[-1]
        self.on_open(abspath)

    def on_open(self, _abspath):
        ...

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if p.endswith(".yml") or isdir:
                tag = "d"
                if p.endswith(".yml"):
                    p = p[0:-4]
                    tag = "f"
                oid = self.tree.insert(parent, 'end', text=p, open=False, tag=tag, values=[abspath])
                if isdir:
                    self.process_directory(oid, abspath)