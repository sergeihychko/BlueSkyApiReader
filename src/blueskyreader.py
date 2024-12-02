import tkinter
from configparser import ConfigParser
from atproto_client import Client
import os

from jupyterlab_server.config import load_config
from pandas.core.interchange.dataframe_protocol import DataFrame

from api_driver import *
from client_wrapper import ClientWrapper
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandas as pd

#TODO fix this hacky way of initializing config file variables
config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..//settings.ini")
# Use the config file
config.read(config_file_path)
account = config.get('main-section', 'account')
token = config.get('main-section', 'api_token')
default_limit = int(config.get('main-section', 'default_limit'))
application_title = config.get('main-section', 'application_title')
database_name = config.get('main-section', 'database_name')


class BlueSkyReader():
    account : str
    token : str
    default_limit : int
    application_title : str
    database_name: str
    df: DataFrame
    client: Client

    def __init__(self, master=None):
        self.df = self.init_data(0)
        self.master = master
        self.current_table_row = -1
        self.createWidgets()
        root.bind('<ButtonRelease-1>', self.clicked)

    def createWidgets(self):
        menu = Menu(root)
        root.config(menu=menu)
        subMenu = Menu(root)
        menu.add_cascade(label="File", menu=subMenu)
        subMenu.add_command(label="Refresh", command=self.do_nothing)
        subMenu.add_separator()
        subMenu.add_command(label="Exit", command=self.master.quit)
        editMenu = Menu(menu)
        menu.add_cascade(labe="Edit", menu=editMenu)
        editMenu.add_command(label="Redo", command=self.do_nothing)

        # toolbar
        toolbar = Frame(root, bg="#747572", relief=tk.RAISED)
        detailButton = Button(toolbar, text="Detail", command=self.create_detail)
        detailButton.pack(side=tk.LEFT, padx=1, pady=1)
        var = StringVar();
        var.set("Select latest limit")
        options = [5, 10, 20, 50, 100]
        option_menu = (OptionMenu(toolbar, var, *(options), command=self.refresh_dataframe)  )
        option_menu.pack(side=tk.LEFT, padx=1, pady=1)
        self.label_limit = Label(root, font="Calibri,12,bold")
        self.label_limit.pack(side=tk.LEFT, padx=1, pady=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.label_limit.pack({"side": "left"})
        # Create a frame for the table
        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        # Create the pandastable
        self.pt = Table(self.frame, dataframe=self.df, showtoolbar=True, showstatusbar=True)
        self.pt.show()

    def create_detail(self):
        if self.current_table_row == -1:
            print("No row currently selefcted.")
        else:
            # preload icon images
            cur_dir = os.getcwd()
            lk_photo = PhotoImage(file=f'{cur_dir}\\assets\\heart-icon.png')
            lk_photo.img = lk_photo
            c2c_photo = PhotoImage(file=f'{cur_dir}\\assets\\c2c-icon.png')
            c2c_photo.img = c2c_photo
            thread_photo = PhotoImage(file=f'{cur_dir}\\assets\\thread-icon.png')
            thread_photo.img = thread_photo
            #create detail window
            detail_window = tkinter.Toplevel()
            detail_window.title("Detail Pane")
            detail_window.geometry("440x280")
            detail_frame = Frame(detail_window)
            detail_frame.pack(fill="both", expand=True)
            row = self.current_table_row
            t = self.df.iloc[row,0]
            d = self.df.iloc[row,1]
            uri = self.df.iloc[row,2]
            text_label = Label(detail_frame, font="Calibri,12,bold", text="Skeet Text:")
            text_label.grid(row=0, column=0, padx=2, pady=2)
            text_data = Label(detail_frame, font="Calibri,12,bold", wraplength=300, text=t)
            text_data.grid(row=0, column=1, padx=2, pady=2)
            time_label = Label(detail_frame, font="Calibri,12,bold", text="Date/Time:")
            time_label.grid(row=1, column=0, padx=2, pady=2)
            time_data = Label(detail_frame, font="Calibri,12,bold", wraplength=300, text=d)
            time_data.grid(row=1, column=1, padx=2, pady=2)
            uriLabel = Label(detail_frame, font="Calibri,12,bold", text="Uri:")
            uriLabel.grid(row=2, column=0, padx=2, pady=2)
            uri_data = Label(detail_frame, font="Calibri,12,bold", wraplength=300, text=uri)
            uri_data.grid(row=2, column=1, padx=2, pady=2)
            uri_button = Button(detail_frame, image=c2c_photo, command=self.c2c(uri))
            uri_button.grid(row=2, column=2, padx=2, pady=2)
            likes_count = 0
            if self.client:
                likes_count = Driver().find_skeet_likes(self.client, uri)
            likes_label = Label(detail_frame, text=likes_count)
            likes_label.grid(row=3, column=1, padx=2, pady=2)
            likes_button = Button(detail_frame, image=lk_photo)
            likes_button.grid(row=3, column=0, padx=2, pady=2)
            thread_count = 0

            if self.client:
                thread_count = Driver().find_skeet_thread(self.client, uri)
            thread_label = Label(detail_frame, text=thread_count)
            thread_label.grid(row=4, column=1, padx=2, pady=2)
            thread_button = Button(detail_frame, image=thread_photo)
            thread_button.grid(row=4, column=0, padx=2, pady=2)

    def refresh_dataframe(self, var):
        page_size = var
        current_page = self.paginate_dataframe(self.df, page_size, 1)
        self.page_df = None
        self.page_df = pd.DataFrame(current_page, columns=['txt', 'time','uri'])
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

    def c2c(self, clip_board_text: str):
        root.clipboard_append((clip_board_text))
        print("clipbaord copied text:" + clip_board_text)

    def clicked(self, event):  # Click event callback function.
        # Probably needs better exception handling, but w/e.
        try:
            clicked = self.pt.get_row_clicked(event)
            self.current_table_row = clicked
        except:
            print('Error on click event')

    def init_data(self, no_api) -> DataFrame:
        """
        Initialize the dataFrame either with
        :param no_api: flag to make API calls or pupulate with dummy data for gui dev
        :return: populated dataFrame object
        """
        # TODO remove after gui testing is complete
        if no_api == 1:
            filler = []
            filler_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cill."
            filler_uri = "at://did:plc:b8aofukbj2iy00gshmk562iu/app.bsky.feed.post/3lbvimzsix22p"
            filler_date = "2024-11-327T19"
            filler.append({'txt': filler_text, 'time': filler_date, 'uri': filler_uri})
            filler.append({'txt': filler_text, 'time': filler_date, 'uri': filler_uri})
            filler.append({'txt': filler_text, 'time': filler_date, 'uri': filler_uri})
            df = pd.DataFrame(filler, columns=['txt', 'time', 'uri'])
        else:
            print("calling api driver :" + account + ":" + token + ":" + str(default_limit))
            client_wrapper = ClientWrapper(account, token)
            self.client = client_wrapper.init_client()
            latest = Driver().perform_get_skeets(self.client)
            df = pd.DataFrame(latest, columns=['txt', 'time', 'uri'])
        return df

if __name__ == "__main__":
    root = Tk()
    app = BlueSkyReader(master=root)
    root.title(application_title)
    root.geometry("650x400")
    root.eval('tk::PlaceWindow . center')
    root.clipboard_clear()
    root.mainloop()




