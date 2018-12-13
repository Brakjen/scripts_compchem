import Tkinter as tk

class ConvertMe(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        frame = tk.Frame(self)
        frame.pack()
        b = tk.Button(frame, text="Exit", command=self.destroy)
        b.pack()

