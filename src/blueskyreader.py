import tkinter
from configparser import ConfigParser
from doctest import master

from atproto_client import Client
import os
import asyncio
import threading
from pandas.core.interchange.dataframe_protocol import DataFrame

from api_driver import *
from scheduler import Scheduler
from client_wrapper import ClientWrapper
from tkinter import *
from tkinter import ttk
import customtkinter as ctk
import tkinter as tk
from pandastable import Table
import pandas as pd
from tkcalendar import Calendar, DateEntry
from tktimepicker import AnalogPicker, constants, SpinTimePickerOld

class BlueSkyReader():
    account : str
    token : str
    default_limit : int
    application_title : str
    database_name: str
    df: DataFrame
    client: Client

    def __init__(self, master=None):
        self.load_config()
        self.df = self.init_data(0)
        self.master = master
        self.current_table_row = -1
        self.createWidgets()
        root.bind('<ButtonRelease-1>', self.clicked)

    def createWidgets(self):
        menu = Menu(root)
        root.config(menu=menu)
        self.subMenu = Menu(root)
        menu.add_cascade(label="File", menu=self.subMenu)
        self.subMenu.add_command(label="Refresh Follower File", command=self.follower_refresh)
        self.subMenu.add_command(label="Refresh Following File", command=self.following_refresh)
        self.subMenu.add_separator()
        self.subMenu.add_command(label="Exit", command=root.quit)
        editMenu = Menu(menu)
        menu.add_cascade(labe="Edit", menu=editMenu)
        editMenu.add_command(label="Detail", command=self.create_detail)
        editMenu.add_command(label="Followers", command=self.create_follower_detail)
        editMenu.add_command(label="Following", command=self.create_following_detail)
        schedMenu = Menu(menu)
        menu.add_cascade(label="Scheduler", menu=schedMenu)
        schedMenu.add_command(label="Detail", command=self.create_schedule_detail)

        # toolbar
        toolbar = ctk.CTkFrame(root)
        detailButton = ctk.CTkButton(toolbar, text="Detail", command=self.create_detail)
        detailButton.pack(side=ctk.LEFT)
        var = StringVar()
        var.set("Select latest limit")
        my_options = ['5', '10', '20', '50', '100']
        option_menu = ctk.CTkOptionMenu(toolbar, variable=var, values=my_options, command=self.refresh_dataframe)
        option_menu.pack(side=tk.LEFT)
        # self.label_limit = ctk.CTkLabel(root)
        # self.label_limit.pack(side=ctk.LEFT)
        follower_detail_button = ctk.CTkButton(toolbar, text="Followers", command=self.create_follower_detail)
        follower_detail_button.pack(side=tk.LEFT, padx=1, pady=1)
        follower_detail_button = ctk.CTkButton(toolbar, text="Following", command=self.create_following_detail)
        follower_detail_button.pack(side=tk.LEFT, padx=1, pady=1)
        self.scheduler_button = ctk.CTkButton(toolbar, text="Scheduler", command=self.start_thread)
        self.scheduler_button.pack(side=tk.RIGHT, padx=1, pady=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Create a frame for the table
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)
        # Create the pandastable
        #self.pt = self.create_tabview_from_dataframe(self.df, master)
        self.pt = Table(self.frame, dataframe=self.df, toolbar=None)
        self.pt.show()
        self.pt.hideRowHeader()

    # def create_tabview_from_dataframe(self, df, master=None):
    #     tabview = ctk.CTkTabview(master=master)
    #     tabview.pack(padx=20, pady=20)
    #     for column in df.columns:
    #         tab = tabview.add(column)
    #         ctk.CTkLabel(tab, text=df[column].to_string()).pack(padx=20, pady=10)
    #     return tabview

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
            detail_window.geometry("460x280")
            detail_frame = Frame(detail_window)
            detail_frame.pack(fill="both", expand=True)
            row = self.current_table_row
            t = self.df.iloc[row,0]
            d = self.df.iloc[row,1]
            uri = self.df.iloc[row,2]
            text_label = Label(detail_frame, font="Calibri,10,bold", text="Skeet Text:")
            text_label.grid(row=0, column=0, padx=2, pady=2)
            text_data = Label(detail_frame, font="Calibri,10,bold", wraplength=300, text=t)
            text_data.grid(row=0, column=1, padx=2, pady=2)
            time_label = Label(detail_frame, font="Calibri,10,bold", text="Date/Time:")
            time_label.grid(row=1, column=0, padx=2, pady=2)
            time_data = Label(detail_frame, font="Calibri,10,bold", wraplength=300, text=d)
            time_data.grid(row=1, column=1, padx=2, pady=2)
            uriLabel = Label(detail_frame, font="Calibri,10,bold", text="Uri:")
            uriLabel.grid(row=2, column=0, padx=2, pady=2)
            uri_data = Label(detail_frame, font="Calibri,10,bold", wraplength=300, text=uri)
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
        current_page = self.paginate_dataframe(self.df, int(page_size), 1)
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

    def create_follower_detail(self):
        #TODO add a detail function and a right click mouse even on this table
        # create follower detail window
        followers_dataframe = pd.read_json(self.followers_json_file)
        detail_f_window = tkinter.Toplevel()
        detail_f_window.title("Follower List : " + str(len(followers_dataframe)))
        detail_f_window.geometry("300x600")
        detail_f_frame = Frame(detail_f_window)
        detail_f_frame.pack(fill="both", expand=True)
        f_table = Table(detail_f_frame, dataframe=followers_dataframe, showtoolbar=True, showstatusbar=True)
        f_table.show()
        detail_f_frame.mainloop()

    def create_following_detail(self):
        #TODO add a detail function and a right click mouse even on this table
        # create following detail window
        following_dataframe = pd.read_json(self.following_json_file)
        detail_fing_window = tkinter.Toplevel()
        detail_fing_window.title("Following List : " + str(len(following_dataframe)))
        detail_fing_window.geometry("300x600")
        detail_fing_frame = Frame(detail_fing_window)
        detail_fing_frame.pack(fill="both", expand=True)
        f_table = Table(detail_fing_frame, dataframe=following_dataframe, showtoolbar=True, showstatusbar=True)
        f_table.show()
        detail_fing_frame.mainloop()

    def create_schedule_detail(self):
        # create schedule detail window
        sched_list = Scheduler.return_task_list()
        self.sched_dataframe = pd.DataFrame(sched_list)
        sched_window = tkinter.Toplevel()
        sched_window.title("Scheduled Tasks")
        sched_window.geometry("600x360")
        self.schedule_table = Table(sched_window, dataframe=self.sched_dataframe, showtoolbar=False, showstatusbar=True)
        self.schedule_table.show()
        self.current_schedule_row = 0
        sched_menu = Menu(sched_window)
        sched_window.config(menu=sched_menu)
        sched_subMenu = Menu(sched_window)
        sched_menu.add_cascade(label="File", menu=sched_subMenu)
        sched_subMenu.add_command(label="New Post", command=self.new_schedule_post)
        sched_subMenu.add_command(label="Edit Post", command=self.edit_schedule_post)
        sched_subMenu.add_separator()
        sched_subMenu.add_command(label="Exit", command=self.do_nothing)
        self.schedule_table.show()
        self.schedule_table.hideRowHeader()

    def new_schedule_post(self):
        #TODO all of this method
        pass

    def edit_schedule_post(self):
        sd_window = tkinter.Toplevel()
        sd_window.title("Detail Pane")
        sd_window.geometry("460x300")
        detail_frame = Frame(sd_window)
        detail_frame.pack(fill="both", expand=True)
        row = self.current_schedule_row
        id = self.sched_dataframe.iloc[row, 0]
        author = self.sched_dataframe.iloc[row, 1]
        uri = self.sched_dataframe.iloc[row, 2]
        txt = self.sched_dataframe.iloc[row, 3]
        queued = self.sched_dataframe.iloc[row, 4]
        queued_date_time = self.sched_dataframe.iloc[row, 5]
        sd_input_frame = Frame(detail_frame)
        sd_id_label = Label(sd_input_frame, font="Calibri,10,bold", text="ID:")
        sd_id_label.grid(row=0, column=0, padx=1, pady=1)
        sd_id__data = Label(sd_input_frame, font="Calibri,10,bold", text=id)
        sd_id__data.grid(row=0, column=1, padx=1, pady=1)
        sd_author_label = Label(sd_input_frame, font="Calibri,10,bold", text="Author")
        sd_author_label.grid(row=1, column=0, padx=1, pady=1)
        sd_author_data = Label(sd_input_frame, font="Calibri,10,bold", text=author)
        sd_author_data.grid(row=1, column=1, padx=1, pady=1)
        sd_uri_label = Label(sd_input_frame, font="Calibri,10,bold", text="uri:")
        sd_uri_label.grid(row=2, column=0, padx=1, pady=1)
        sd_uri_data = Label(sd_input_frame, font="Calibri,10,bold", text=uri)
        sd_uri_data.grid(row=2, column=1, padx=1, pady=1)
        sd_body_label = Label(sd_input_frame, font="Calibri,10,bold", text="Body:")
        sd_body_label.grid(row=3, column=0, padx=1, pady=1)
        sd_body_data = Text(sd_input_frame, font="Calibri,10,bold", width=40, height=8)
        sd_body_data.insert("1.0",txt)
        sd_body_data.grid(row=3, column=1, padx=1, pady=1)
        sd_input_frame.grid(row=0, column=0)
        #
        sd_queued_panel = Frame(detail_frame)
        sd_queued_label = Label(sd_queued_panel, font="Calibri,10,bold", text="Queued:")
        sd_queued_label.pack(side=tk.LEFT)
        queued_var = tk.StringVar(value="True")
        queued_combo = ttk.Combobox(sd_queued_panel, width=27, values=('True', 'False'), textvariable=queued_var)
        queued_combo.pack(side=tk.LEFT)
        sd_queued_panel.grid(row=1, column=0, padx=1, pady=1)
        #
        sd_queued_display_panel = Frame(detail_frame)
        sd_queued_date_label = Label(sd_queued_display_panel, font="Calibri,10,bold", text="Date/Time:")
        sd_queued_date_label.pack(side=tk.LEFT)
        sd_queued_date_data = Label(sd_queued_display_panel, font="Calibri,10,bold", text=queued_date_time)
        sd_queued_date_data.pack(side=tk.LEFT)
        sd_queued_date_show = Button(sd_queued_display_panel, font="Calibri,10,bold", text='Date/Time Widgets', command=self.time_date_widgets)
        sd_queued_date_show.pack(side=tk.LEFT)
        sd_queued_display_panel.grid(row=2, column=0, padx=1, pady=1)
        global t_d_p_window # To access the Time/Date widget window outside the function
        self.t_d_p_window= None
        #TODO need the code behind time/date changes in the widget reflecting in the data row.

    def time_date_widgets(self):
        if self.t_d_p_window is None or not self.t_d_p_window.winfo_exists():
            t_d_p_window = tkinter.Toplevel()
            t_d_p_window.title("Time Selector")
            t_d_p_window.geometry("560x260")
            sd_queued_time_panel = Frame(t_d_p_window)
            sd_cal = Calendar(sd_queued_time_panel, font="Calibri,10", selectmode='day', locale='en_US',
                              cursor="hand1", year=2024, month=12, day=4)
            sd_cal.pack(side=tk.LEFT)
            sd_cal.bind("<<DateEntrySelected>>", self.on_date_select)
            sd_time_picker = AnalogPicker(sd_queued_time_panel)
            sd_time_picker.pack(side=tk.LEFT)
            sd_time_picker.bind("<<TimeChanged>>", self.on_time_change)
            sd_queued_time_panel.pack()


    def on_time_change(self, event):
        print("time change :", event.widget.get_time())

    def on_date_select(self, event):
        print("date change :", event.widget.get_date())

    def sel_queued(self):
        pass

    def follower_refresh(self):
        self.subMenu.entryconfig("Refresh Follower File", state="disabled")
        threading.Thread(target=self.run_async_follower_dump).start()

    def run_async_follower_dump(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(Driver().create_follower_json(self.client, self.account, self.followers_json_file))
        self.subMenu.entryconfig("Refresh Follower File", state="normal")

    def following_refresh(self):
        self.subMenu.entryconfig("Refresh Following File", state="disabled")
        threading.Thread(target=self.run_async_following_dump).start()

    def run_async_following_dump(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(Driver().create_following_json(self.client, self.account, self.following_json_file))
        self.subMenu.entryconfig("Refresh Following File", state="normal")

    def do_nothing(self):
        pass

    def start_thread(self):
        #TODO thread lifecycle managment needed, this is just a WIP implementation
        self.scheduler_button.config(state="disabled")
        thread = Scheduler("My Scheduler Daemon Thread")
        thread.start()

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

    def load_config(self):
        config = ConfigParser()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(script_dir, "..//settings.ini")
        # Use the config file
        config.read(config_file_path)
        self.account = config.get('main-section', 'account')
        self.token = config.get('main-section', 'api_token')
        self.default_limit = int(config.get('main-section', 'default_limit'))
        self.application_title = config.get('main-section', 'application_title')
        self.database_name = config.get('main-section', 'database_name')
        self.followers_json_file = config.get('main-section', 'followers_json_file')
        self.following_json_file = config.get('main-section', 'following_json_file')

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
            client_wrapper = ClientWrapper(self.account, self.token)
            self.client = client_wrapper.init_client()
            latest = Driver().perform_get_skeets(self.client)
            df = pd.DataFrame(latest, columns=['txt', 'time', 'uri'])
        return df

if __name__ == "__main__":
    root = Tk()
    app = BlueSkyReader(master=root)
    root.title(app.application_title)
    root.geometry("700x400")
    root.eval('tk::PlaceWindow . center')
    root.clipboard_clear()
    root.mainloop()




