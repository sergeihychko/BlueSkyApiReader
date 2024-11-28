from configparser import ConfigParser
import os
from api_driver import *
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
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

        # Create the variables
        var = StringVar();
        var.set("Select latest limit")
        options = [5,10,20,50,100]
        OptionMenu(root, var, *(options), command=self.refresh_dataframe).pack(pady=50)
        self.label_limit = Label(root, font="Calibri,12,bold")
        self.label_limit.pack(padx=20, pady=20)

        self.label_limit.pack({"side": "left"})
        # Create a frame for the table
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        # Create the pandastable
        self.pt = Table(self.frame, dataframe=self.df, showtoolbar=True, showstatusbar=True)
        self.pt.show()

    def __init__(self, df, master=None):
        Frame.__init__(self, master)
        self.df = df
        self.pack()
        self.createWidgets()

    def refresh_dataframe(self, var):
        page_size = var
        # latest = driver_object.perform_get_skeets(account, token)
        # full_df = pd.DataFrame(latest, columns=['uri', 'txt'])
        current_page = self.paginate_dataframe(self.df, page_size, 1)
        self.page_df = None
        self.page_df = pd.DataFrame(current_page, columns=['uri', 'txt'])
        if self.page_df.empty:
            print("The DataFrame is empty!")
        self.pt.model.df = self.page_df
        self.pt.redraw()

    def paginate_dataframe(self, df, page_size=10, page_num=1):
        start_index = (page_num - 1) * page_size
        end_index = start_index + page_size
        print("returning paginated dataframe")
        return df.iloc[start_index:end_index]

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
latest = driver_object.perform_get_skeets(account, token)
df = pd.DataFrame(latest, columns=['uri', 'txt'])

#gui definitions
root = Tk()
root.title (application_title)
root.geometry("400x300")
app = BlueSkyReader(df, master=root)
app.mainloop()
root.destroy()



