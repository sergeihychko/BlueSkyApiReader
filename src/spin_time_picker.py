import tkinter as tk

class SpinTimePicker(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master)

        self.hour = tk.StringVar(value=12)
        self.minute = tk.StringVar(value=0)
        self.seconds = tk.StringVar(value=0)

        # Update attributes based on keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.hour_spinbox = tk.Spinbox(self, from_=0, to=23, width=2, textvariable=self.hour)
        self.hour_spinbox.pack(side="left", padx=5)
        self.hour_spinbox.delete(0, tk.END)
        self.hour_spinbox.insert(0, str(self.hour))

        tk.Label(self, text=":").pack(side="left")

        self.minute_spinbox = tk.Spinbox(self, from_=0, to=59, width=2, textvariable=self.minute)
        self.minute_spinbox.pack(side="left", padx =5)
        self.minute_spinbox.delete(0, tk.END)
        self.minute_spinbox.insert(0, str(self.minute))

        tk.Label(self, text=":").pack(side="left")

        self.seconds_spinbox = tk.Spinbox(self, from_=0, to=59, width=2, textvariable=self.seconds)
        self.seconds_spinbox.pack(side="left", padx=5)
        self.seconds_spinbox.delete(0, tk.END)
        self.seconds_spinbox.insert(0, str(self.seconds))

    def get_time(self):
        return f"{self.hour}:{self.minute}:{self.seconds}"