# -*- coding: utf-8 -*-
"""@package mte.gui
Graphical user interface for Medusa Testing Environment
"""
import Tkinter as Tk
import sys
import ttk as ttk

import tpm
from config import testing_suites
from config import tests


# mainframe = Frame(root, padding="3 3 12 12")
# for child in mainframe.winfo_children():
#     child.grid_configure(padx=5, pady=5)


class Mte(Tk.Frame):
    """
    Main window
    """
    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the window and creates basic GUI elements.
        @param parent: Tk window object
        @param args: not used
        @param kwargs: not used
        """
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.grid(column=0, row=0, sticky=(Tk.N, Tk.W, Tk.E, Tk.S))
        self.columnconfigure(0, weight=0)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.text = Tk.Text(self)
        sys.stdout = StdRedirect(self.text)
        self.left_frame = Tk.Frame(self)
        self.calls_frame = ttk.LabelFrame(self.left_frame, text="System calls")
        self.tests_frame = ttk.LabelFrame(self.left_frame, text="Test suites")
        self.checkbuttons = []
        self.checkbuttons_suite = []
        # For some strange reason we have to keep reference on checkbutton variables,
        # otherwise they will show the third state
        self.checkbutton_vars = []
        self.checkbutton_suite_vars = []
        self.create_checkbuttons()
        self.select_all = ttk.Button(self.calls_frame, text='Select all', command=lambda: self.selection(1))
        self.deselect_all = ttk.Button(self.calls_frame, text='Deselect all', command=lambda: self.selection(0))
        self.start = ttk.Button(self.left_frame, text='Start testing', command=self.start_testing)
        self.grid_widgets()

    def grid_widgets(self):
        """
        Positions GUI elements in their respective place on the grid
        """
        options = dict(sticky=(Tk.N, Tk.S, Tk.E, Tk.W), padx=3, pady=4)
        self.text.grid(column=1, row=0, **options)
        self.left_frame.grid(column=0, row=0, **options)
        self.calls_frame.grid(column=0, row=0, **options)
        self.tests_frame.grid(column=0, row=1, **options)
        for i, checkbutton in enumerate(self.checkbuttons):
            checkbutton.grid(column=0, row=i, **options)
        self.select_all.grid(column=0, row=i + 1, **options)
        self.deselect_all.grid(column=0, row=i + 2, **options)
        for i, checkbutton in enumerate(self.checkbuttons_suite):
            checkbutton.grid(column=0, row=i, **options)
        self.start.grid(column=0, row=2, **options)

    def create_checkbuttons(self):
        """
        Creates checkbuttons for each test and suite
        """
        for test in tests:
            var = Tk.IntVar()
            var.set(1)
            c = ttk.Checkbutton(self.calls_frame, text=test, variable=var)
            self.checkbutton_vars.append(var)
            self.checkbuttons.append(c)
        for suite in testing_suites:
            var = Tk.IntVar()
            var.set(1)
            c = ttk.Checkbutton(self.tests_frame, text=suite, variable=var)
            self.checkbutton_suite_vars.append(var)
            self.checkbuttons_suite.append(c)

    def start_testing(self):
        """
        Called after the button is pressed.
        Calls tpm module with a list of tests and suites to be executed.
        """
        test_list = []
        suite_list = []
        for checkbutton in self.checkbuttons:
            if checkbutton.state() == ('selected',):
                test_list.append(checkbutton['text'])
        for checkbutton in self.checkbuttons_suite:
            if checkbutton.state() == ('selected',):
                suite_list.append(testing_suites[checkbutton['text']])
        tpm.main(test_list, suite_list)
        # TODO Add disable when testing, check for output and decide based on that

    def selection(self, state):
        """
        Selects tests checkbuttons
        @param state: 1 for select all, 0 for deselect all
        @return: none
        """
        for var in self.checkbutton_vars:
            var.set(state)


class StdRedirect(object):
    """
    Standard output redirection for the GUI.
    """
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(Tk.END, string)
        self.widget.see(Tk.END)
    # TODO How about some interaction?

if __name__ == "__main__":
    root = Tk.Tk()
    root.title("Medusa testing environment")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    Mte(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
