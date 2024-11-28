from configparser import ConfigParser
import os
from api_driver import *
from tkinter import *
from tkinter import ttk
import pandas as pd

class BlueSkyReader(Frame):
    def say_hi(self):
        print("hi there, everyone!")

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})
        self.tree = ttk.Treeview(self.master, columns=list(self.df.columns), show="headings")
        for col in self.df.columns:
            self.tree.heading(col, text=col)
        for index, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row))
        self.tree.pack()

    def __init__(self, df, master=None):
        Frame.__init__(self, master)
        self.df = df
        self.pack()
        self.createWidgets()


account = ""
token = ""
default_limit = 0
application_title = ""
database_name = ""

# load configuration options
print("loading config")
config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..//settings.ini")
# Use the config file
config.read(config_file_path)
account = config.get('main-section', 'account')
token = config.get('main-section', 'api_token')
default_limit = config.get('main-section', 'default_limit')
application_title = config.get('main-section', 'application_title')
database_name = config.get('main-section', 'database_name')
print("calling api driver :" + account + ":" + token + ":" + default_limit)
driver_object = Driver()
latest = driver_object.perform_get_skeets(account, token, default_limit)
df = pd.DataFrame(latest, columns=['uri', 'txt'])

#gui definitions
root = Tk()
root.title (application_title)
root.geometry("400x300")
app = BlueSkyReader(df, master=root)
app.mainloop()
root.destroy()



