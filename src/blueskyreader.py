import tkinter
from configparser import ConfigParser
from atproto_client import Client
import os
from api_driver import *
from client_wrapper import ClientWrapper
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandas as pd

class BlueSkyReader(Frame):

    def createWidgets(self):
        self.current_table_row=-1
        menu = Menu(root)
        root.config(menu=menu)
        subMenu = Menu(root)
        menu.add_cascade(label="File", menu=subMenu)
        subMenu.add_command(label="Refresh", command=self.do_nothing)
        subMenu.add_separator()
        subMenu.add_command(label="Exit", command=self.quit)
        editMenu = Menu(menu)
        menu.add_cascade(labe="Edit", menu=editMenu)
        editMenu.add_command(label="Redo", command=self.do_nothing)

        # toolbar
        toolbar = Frame(root, bg="#747572", relief=tk.RAISED)
        detailButton = Button(toolbar, text="Detail", command=self.create_detail)
        detailButton.pack(side=tk.LEFT, padx=1, pady=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)

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
        root.bind('<ButtonRelease-1>', self.clicked)

    def create_detail(self):
        if self.current_table_row == -1:
            print("No row currently selefcted.")
        else:
            print("opening the detail window.")
            detail_window = tkinter.Toplevel()
            detail_window.title("Detail Pane")
            detail_window.geometry("400x400")
            detail_frame = Frame(detail_window)
            detail_frame.pack(fill="both", expand=True)
            row = self.current_table_row
            t = self.df.iloc[row,0]
            d = self.df.iloc[row,1]
            uri = self.df.iloc[row,2]
            textLabel = Label(detail_frame, font="Calibri,12,bold", wraplength=300, text=t)
            textLabel.pack(side=tk.TOP, padx=2, pady=2)
            timeLabel = Label(detail_frame, font="Calibri,12,bold", wraplength=300, text=d)
            timeLabel.pack(side=tk.TOP,padx=2, pady=2)
            uriLabel = Label(detail_frame, font="Calibri,12,bold", wraplength=300, text=uri)
            uriLabel.pack(side=tk.TOP,padx=2, pady=2)
            likes_count = 0
            if c:
                likes_count = Driver().find_skeet_likes(c, uri)
            likes_label = Label(detail_frame, text=likes_count).pack(side=tk.LEFT)
            cur_dir = os.getcwd()
            photo = PhotoImage(file=f'{cur_dir}\\assets\\heart-icon.png')
            photo.img = photo
            likesButton = Button(detail_frame, image=photo).pack(side=tk.LEFT)

            #print(self.df)

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

    def do_nothing(self):
        pass

    def clicked(self, event):  # Click event callback function.
        # Probably needs better exception handling, but w/e.
        try:
            rclicked = self.pt.get_row_clicked(event)
            self.current_table_row = rclicked
            cclicked = self.pt.get_col_clicked(event)
            clicks = (rclicked, cclicked)
            print('clicks:', clicks)
        except:
            print('Error')

application_title = ""
database_name = ""
#TODO remove after gui testing is complete
no_api = 0
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
# try:
if no_api == 1:
    filler = []
    filler.append({'date': 'date1', 'txt': 'dummy text', 'uri': 'dummy uri'})
    filler.append({'date': 'date2', 'txt': 'dummy text2', 'uri': 'dummy uri2'})
    filler.append({'date': 'date2', 'txt': 'dummy text3', 'uri': 'dummy uri3'})
    df = pd.DataFrame(filler, columns=['date', 'txt', 'uri'])
else:
    print("calling api driver :" + account + ":" + token + ":" + default_limit)
    client_wrapper = ClientWrapper(account, token)
    c = client_wrapper.init_client()
    latest = Driver().perform_get_skeets(c)
    df = pd.DataFrame(latest, columns=['txt','time', 'uri'])
# except Exception as e:
#     print(e)

#gui definitions
root = Tk()
root.title (application_title)
root.geometry("600x500")
app = BlueSkyReader(df, master=root)
app.mainloop()
root.destroy()



