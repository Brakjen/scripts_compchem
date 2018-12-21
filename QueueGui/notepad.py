import Tkinter as tk
import tkFont
import os
from datetime import datetime

class NotePad(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("NotePad")

        self.notepath = "/home/ambr/.queuegui/notepad_notes.txt"

        self["bg"] = self.parent.maincolor

        self.buttonfont = tkFont.Font(family="arial", size=10)
        self.notefont = tkFont.Font(family="arial", size=12)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.place_widgets()
        self.load_notes()

        
    def place_widgets(self):
        self.top = tk.Frame(self, bg=self.parent.maincolor)
        self.frame = tk.Frame(self, bg=self.parent.maincolor)
        self.bot = tk.Frame(self, bg=self.parent.maincolor)

        self.frame.grid(row=1, column=0, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        self.top.grid(row=0, column=0)
        self.bot.grid(row=2, column=0)

        yscrollbar = tk.Scrollbar(self.frame)
        self.text = tk.Text(self.frame, yscrollcommand=yscrollbar.set, font=self.notefont)
        yscrollbar.grid(row=0, column=1, padx=2, pady=2, sticky="ns")
        self.text.grid(row=0, column=0, columnspan=3, sticky="nsew")

        yscrollbar.configure(command=self.text.yview)

        b_save = tk.Button(self.bot, text="Save Notes", pady=5, padx=5, command=self.save)
        b_save.grid(row=1, column=0, sticky="w")

        b_exit_not_save = tk.Button(self.bot, text="Exit Without Saving", pady=5, padx=5, command=self.exit_not_save)
        b_exit_not_save.grid(row=1, column=2, sticky="w")

        b_save_and_exit = tk.Button(self.bot, text="Save And Exit", pady=5, padx=5, command=self.save_and_exit)
        b_save_and_exit.grid(row=1, column=1, sticky="w")

    def load_notes(self):
        try:
            with open(self.notepath, "r") as f:
                notes = f.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, notes)
        except IOError:
            self.parent.log_update("Notes not found. Generating new file.")
            with open(self.notepath, "w") as f:
                f.write("\n")
        return

    def save(self):
        with open(self.notepath, "w") as f:
            f.write(self.text.get(1.0, tk.END))
            self.parent.log_update("Notes written.")
        return

    def save_and_exit(self):
        with open(self.notepath, "w") as f:
            f.write(self.text.get(1.0, tk.END))
            self.parent.log_update("Notes written.")
        self.destroy()

    def exit_not_save(self):
        self.destroy()

