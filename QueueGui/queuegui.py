#!/usr/bin/env python

import Tkinter as tk
from mainwindow import MainWindow
from convertme import ConvertMe
from toolbox import ToolBox

class QueueGui(tk.Tk):
    """Docstring"""

    def __init__(self, *args, **kwargs):
        """Docstring"""
        tk.Tk.__init__(self, *args, **kwargs)

        self["bg"] = "dark slate gray"
        
        main_window = MainWindow(self)

        self.title("Queue-Gui")

    def launch_convertme(self):
        pass

    def launch_toolbox(self):
        pass






###################################
# run application
if __name__ == "__main__":
    app = QueueGui()
    app.mainloop()
###################################
