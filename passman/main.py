import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

from ttkthemes import ThemedTk

import yaml

from .events import ErrorEvent, WriteEvent
from .file_tree import FileTree
from .flat_editor import FlatEditor
from .pubsub import pubsub
from .queue_writer import QueueWriter


def escapable(master):
    master.bind("<Control-w>", lambda _e: master.quit())
    master.bind("<Escape>", lambda _e: master.quit())


class MainWindow(tk.Frame):
    def __init__(self, master, path):
        escapable(master)

        super().__init__(master, borderwidth=5)

        self.pack(fill=tk.BOTH, expand=1)
        self.left = FileTree(self, path)
        self.left.on_open = self.open_file
        self.right = FlatEditor(self)

        self.left.pack(side=tk.LEFT, fill=tk.Y, anchor="nw")
        self.right.pack(side=tk.TOP, fill=tk.BOTH, expand=1, after=self.left)
        self.current_path = None
        self.memo = {}
        self.write_q = QueueWriter()
        self.write_q.start()

        pubsub.subscribe(ErrorEvent, self.error_event)
        pubsub.subscribe(WriteEvent, self.write_event)

    @staticmethod
    def error_event(msg):
        print(msg)

    @staticmethod
    def write_event(msg):
        print(msg)

    def open_file(self, path):
        if self.current_path:
            user_data = self.right.get_data()
            current_data = self.memo.get(self.current_path)
            if user_data != current_data:
                self.write_q.write(self.current_path, yaml.dump(user_data))
                self.memo[self.current_path] = user_data

        self.current_path = path

        title = os.path.basename(path)
        title, _ = os.path.splitext(title)

        if path not in self.memo:
            with open(path) as fh:
                data = yaml.safe_load(fh)
            self.memo[path] = data
        else:
            data = self.memo[path]

        self.right.set_data(title, data)

    def done(self):
        self.write_q.stop()
        self.write_q.join()


def main():
    THEME = "blue"

    if THEME in ThemedTk.pixmap_themes:
        root = ThemedTk(theme=THEME)
    else:
        root = tk.Tk()
        ttk.Style(root).theme_use(THEME)

    root.title("Password Manager for Encrypted Mount")

    assets = Path(__file__).parent / "assets"

    photo = tk.PhotoImage(file=assets / "icon.png")
    root.iconphoto(False, photo)

    path_to_my_project = sys.argv[-1]

    sup = MainWindow(root, path=path_to_my_project)

    try:
        sup.mainloop()
    finally:
        sup.done()
        pubsub.shutdown(wait=False)

