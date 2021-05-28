from __future__ import print_function

from tkinter import END

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


class DateEntryBetter(tk.Frame):
    def __init__(self, master, frame_look={}, **look):
        args = dict()
        args.update(frame_look)
        tk.Frame.__init__(self, master, **args)

        self.entry_1 = tk.Entry(self, width=2, **args)
        self.label_1 = tk.Label(self, text='/', **args)
        self.entry_2 = tk.Entry(self, width=2, **args)
        self.label_2 = tk.Label(self, text='/', **args)
        self.entry_3 = tk.Entry(self, width=4, **args)

        self.entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.entry_3.pack(side=tk.LEFT)

        self.entries = [self.entry_1, self.entry_2, self.entry_3]

        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 4))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, cont[:-1])

    def _check(self, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        if len(data) > size or not data.isdigit():
            self._backspace(entry)
        if len(data) >= size and next_entry:
            next_entry.focus()

    def get(self):
        return [e.get() for e in self.entries]

    def delete(self, first_index, last_index):
        for e in self.entries:
            e.delete(first_index, last_index)

    def insert(self, first_index, date_list):
        i = 0
        for e in self.entries:
            e.insert(first_index, date_list[i])
            i += 1

    def set_state(self, new_state):
        for e in self.entries:
            e.config(state=new_state)


if __name__ == '__main__':
    win = tk.Tk()
    win.title('DateEntry demo')

    dentry = DateEntryBetter(win, font=('Helvetica', 40, tk.NORMAL), border=0)
    dentry.pack()

    win.bind('<Return>', lambda e: print(dentry.get()))
    win.mainloop()
