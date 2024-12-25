import datetime
import tkinter
from configparser import ConfigParser
from doctest import master

from atproto_client import Client
import os
import asyncio
import threading
import logging
from utilities import WebImage
from PIL import ImageTk

from customtkinter import CTkLabel
from pandas.core.interchange.dataframe_protocol import DataFrame

from api_driver import *
from scheduler import Scheduler
from database_driver import *
from post_data import PostData
from profile import ProfileData
from client_wrapper import ClientWrapper
from tkinter import *
from tkinter import ttk, messagebox
import customtkinter as ctk
import tkinter as tk
from pandastable import Table
import pandas as pd
from tkcalendar import Calendar, DateEntry
from spin_time_picker import SpinTimePicker

class BlueSkyReader():
    account : str
    token : str
    default_limit : int
    application_title : str
    database_name: str
    df: DataFrame
    client: Client
    profile : ProfileData
    format_string = "%Y-%m-%d %H:%M:%S"

    def __init__(self, master=None):
        self.load_config()
        self.df = self.init_data(0)
        self.master = master
        self.current_table_row = -1
        self.current_schedule_row = -1
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
        profileMenu = Menu(menu)
        menu.add_cascade(label="Profile", menu=profileMenu)
        profileMenu.add_command(label="Detail", command=self.create_profile_detail)
        # toolbar
        toolbar = ctk.CTkFrame(root)
        detailButton = ctk.CTkButton(toolbar, text="Detail", command=self.create_detail)
        detailButton.pack(side=ctk.LEFT)
        var = StringVar()
        var.set("Select latest limit")
        my_options = ['5', '10', '20', '50', '100']
        option_menu = ctk.CTkOptionMenu(toolbar, variable=var, values=my_options, command=self.refresh_dataframe)
        option_menu.pack(side=tk.LEFT)
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
        self.pt = Table(self.frame, dataframe=self.df, toolbar=None)
        self.pt.show()
        self.pt.hideRowHeader()

    def create_detail(self):
        if self.current_table_row == -1:
            logging.debug("No row currently selected.")
            messagebox.showinfo("Information", "No row currently selected.")
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
            detail_frame = ctk.CTkFrame(detail_window)
            detail_frame.pack(fill="both", expand=True)
            row = self.current_table_row
            t = self.df.iloc[row,0]
            d = self.df.iloc[row,1]
            uri = self.df.iloc[row,2]
            text_label = CTkLabel(detail_frame, text="Skeet Text:")
            text_label.grid(row=0, column=0, padx=2, pady=2)
            text_data = CTkLabel(detail_frame, wraplength=300, text=t)
            text_data.grid(row=0, column=1, padx=2, pady=2)
            time_label = CTkLabel(detail_frame, text="Date/Time:")
            time_label.grid(row=1, column=0, padx=2, pady=2)
            time_data = CTkLabel(detail_frame, wraplength=300, text=d)
            time_data.grid(row=1, column=1, padx=2, pady=2)
            uriLabel = CTkLabel(detail_frame, text="Uri:")
            uriLabel.grid(row=2, column=0, padx=2, pady=2)
            uri_data = CTkLabel(detail_frame, wraplength=300, text=uri)
            uri_data.grid(row=2, column=1, padx=2, pady=2)
            uri_button = Button(detail_frame, image=c2c_photo, command=self.c2c(uri))
            uri_button.grid(row=2, column=2, padx=2, pady=2)
            likes_count = 0
            try:
                if self.client:
                    likes_count = Driver().find_skeet_likes(self.client, uri)
                likes_label = CTkLabel(detail_frame, text=likes_count)
                likes_label.grid(row=3, column=1, padx=2, pady=2)
                likes_button = Button(detail_frame, image=lk_photo)
                likes_button.grid(row=3, column=0, padx=2, pady=2)
                thread_count = 0
            except:
                pass
            try:
                if self.client:
                    thread_count = Driver().find_skeet_thread(self.client, uri)
                thread_label = CTkLabel(detail_frame, text=thread_count)
                thread_label.grid(row=4, column=1, padx=2, pady=2)
                thread_button = Button(detail_frame, image=thread_photo)
                thread_button.grid(row=4, column=0, padx=2, pady=2)
            except:
                pass

    def refresh_dataframe(self, var):
        page_size = var
        current_page = self.paginate_dataframe(self.df, int(page_size), 1)
        self.page_df = None
        self.page_df = pd.DataFrame(current_page, columns=['txt', 'time','uri'])
        if self.page_df.empty:
            logging.debug("The DataFrame is empty!")
        self.pt.model.df = self.page_df
        self.pt.redraw()

    def paginate_dataframe(self, df, page_size=10, page_num=1):
        start_index = (page_num - 1) * page_size
        end_index = start_index + page_size
        logging.debug("returning paginated dataframe")
        return df.iloc[start_index:end_index]

    def create_follower_detail(self):
        #TODO add a detail function and a right click mouse even on this table
        # create follower detail window
        followers_dataframe = pd.read_json(self.followers_json_file)
        detail_f_window = tkinter.Toplevel()
        detail_f_window.title("Follower List : " + str(len(followers_dataframe)))
        detail_f_window.geometry("300x600")
        detail_f_frame = ctk.CTkFrame(detail_f_window)
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
        detail_fing_frame = ctk.CTkFrame(detail_fing_window)
        detail_fing_frame.pack(fill="both", expand=True)
        f_table = Table(detail_fing_frame, dataframe=following_dataframe, showtoolbar=True, showstatusbar=True)
        f_table.show()
        detail_fing_frame.mainloop()

    def create_profile_detail(self):
        # create profile detail window
        detail_profile_window = tkinter.Toplevel()
        detail_profile_window.title("Following List : " + str(self.profile.displayName))
        detail_profile_window.geometry("300x600")
        detail_profile_frame = ctk.CTkFrame(detail_profile_window)
        detail_profile_frame.pack(fill="both", expand=True)
        profile_image = WebImage(self.profile.avatar_uri).get()
        #TODO obviously reserach resizing this photo
        #profile_image_button = Button(detail_profile_frame, image=profile_image, width=50, height=50)
        #profile_image_button.pack(side=tk.LEFT)
        profile_dn_label = CTkLabel(detail_profile_frame, text=self.profile.displayName)
        profile_dn_label.pack(side=tk.LEFT)
        profile_des_label = CTkLabel(detail_profile_frame, text=self.profile.description)
        profile_des_label.pack(side=tk.LEFT)
        detail_profile_window.mainloop()

    def create_schedule_detail(self):
        # create schedule detail window
        sched_list = Scheduler.return_task_list()
        self.sched_dataframe = pd.DataFrame(sched_list)
        sched_window = tkinter.Toplevel()
        sched_window.title("Scheduled Tasks")
        sched_window.geometry("600x360")
        sched_window.bind('<ButtonRelease-1>', self.scheduler_clicked)
        sched_menu = Menu(sched_window)
        sched_window.config(menu=sched_menu)
        self.subMenu = Menu(sched_window)
        sched_window.config(menu=sched_menu)
        sched_subMenu = Menu(sched_window)
        sched_menu.add_cascade(label="File", menu=sched_subMenu)
        sched_subMenu.add_separator()
        sched_editMenu = Menu(sched_window)
        sched_subMenu.add_command(label="Exit", command=self.do_nothing)
        sched_menu.add_cascade(label="Edit", menu=sched_editMenu)
        sched_editMenu.add_command(label="New Post", command=self.new_schedule_post)
        sched_editMenu.add_command(label="Edit Post", command=self.edit_schedule_post)
        sched_editMenu.add_command(label="Delete Post", command=self.delete_schedule_post)
        # toolbar
        sched_toolbar = ctk.CTkFrame(sched_window)
        sched_toolbar.pack(side=tk.TOP, fill=tk.X)
        sched_newButton = ctk.CTkButton(sched_toolbar, text="Delete", command=self.new_schedule_post)
        sched_newButton.pack(side=ctk.LEFT)
        sched_editButton = ctk.CTkButton(sched_toolbar, text="Delete", command=self.edit_schedule_post)
        sched_editButton.pack(side=ctk.LEFT)
        sched_deleteButton = ctk.CTkButton(sched_toolbar, text="Delete", command=self.delete_schedule_post)
        sched_deleteButton.pack(side=ctk.LEFT)
        sched_deleteButton = ctk.CTkButton(sched_toolbar, text="Refresh", command=self.refresh_schedule_table)
        sched_deleteButton.pack(side=ctk.RIGHT)
        # frame
        sched_frame = ctk.CTkFrame(sched_window)
        # table
        self.schedule_table = Table(sched_frame, dataframe=self.sched_dataframe, showtoolbar=False, showstatusbar=False)
        self.schedule_table.show()
        self.schedule_table.hideRowHeader()
        sched_frame.pack(fill="both", expand=True)
        self.schedule_table.show()
        self.schedule_table.hideRowHeader()

    def new_schedule_post(self):
        sd_n_window = tkinter.Toplevel()
        sd_n_window.title("Detail Pane")
        sd_n_window.geometry("500x260")
        detail_frame = ctk.CTkFrame(sd_n_window)
        detail_frame.pack(fill="both", expand=True)
        author =self.account
        uri = ""
        txt = ""
        queued = False
        self.sdn_queued_date_time = datetime.datetime.now()
        #queued_date_time = datetime.datetime.now()
        sd_n_input_frame = ctk.CTkFrame(detail_frame)
        sd_n_author_label = CTkLabel(sd_n_input_frame, text="Author:")
        sd_n_author_label.grid(row=0, column=0, padx=1, pady=1)
        sd_n_author_data = CTkLabel(sd_n_input_frame, text=author)
        sd_n_author_data.grid(row=0, column=1, padx=1, pady=1)
        sd_n_body_label = CTkLabel(sd_n_input_frame, text="Body:")
        sd_n_body_label.grid(row=1, column=0, padx=1, pady=1)
        self.sd_n_body_data = Text(sd_n_input_frame, width=40, height=8)
        self.sd_n_body_data.insert("1.0", txt)
        self.sd_n_body_data.grid(row=1, column=1, padx=1, pady=1)
        sd_n_image_label = CTkLabel(sd_n_input_frame, text="Attachments:")
        sd_n_image_label.grid(row=2, column=0, padx=1, pady=1)
        sd_n_image_data = Button(sd_n_input_frame, text="Click to select attachment")
        sd_n_image_data.grid(row=2, column=1, padx=1, pady=1)
        sd_n_input_frame.grid(row=0, column=0)
        #
        sd_n_queued_display_panel = ctk.CTkFrame(detail_frame)
        sd_n_queued_date_label = CTkLabel(sd_n_queued_display_panel, text="Date/Time:")
        sd_n_queued_date_label.pack(side=tk.LEFT)
        self.sd_n_queued_date_data = CTkLabel(sd_n_queued_display_panel, text=str(self.sdn_queued_date_time))
        self.sd_n_queued_date_data.pack(side=tk.LEFT)
        sd_n_queued_date_show = ctk.CTkButton(sd_n_queued_display_panel, text='Date/Time Widgets',
                                     command=self.time_date_new_widgets)
        sd_n_queued_date_show.pack(side=tk.LEFT)
        sd_n_queued_display_panel.grid(row=2, column=0, padx=1, pady=1)
        self.new_task = PostData(None, author, None, "", queued, self.sdn_queued_date_time)
        sd_n_submit_button = ctk.CTkButton(detail_frame, text='Save Sceduled Task',
                                  command=self.save_scheduled_task)
        sd_n_submit_button.grid(row=3, column=0)
        global n_t_d_p_window  # To access the Time/Date widget window outside the function
        self.n_t_d_p_window = None

    def refresh_schedule_table(self):
        current_sched_list = Scheduler.return_task_list()
        self.sched_dataframe = pd.DataFrame(current_sched_list)

    def delete_schedule_post(self):
        if self.current_schedule_row == -1:
            logging.debug("No row currently selected.")
            messagebox.showinfo("Information", "No row currently selected.")
        else:
            delete_index = self.sched_dataframe.iloc[int(self.current_schedule_row), 0]
            response = messagebox.askquestion("Question", "Do you want to delete Scheduled Task :" + delete_index + "?")
            if response == 'yes':
                commit = delete_scheduled_post(delete_index)
                if commit:
                    messagebox.showinfo("Information", "Task was deleted successfully")
                else:
                    messagebox.showinfo("Information", "Error while deleting task")
            else:
                logging.debug("Aborted delete_scheduled_post")

    def edit_schedule_post(self):
        sd_window = tkinter.Toplevel()
        sd_window.title("Detail Pane")
        sd_window.geometry("470x340")
        detail_frame = ctk.CTkFrame(sd_window)
        detail_frame.pack(fill="both", expand=True)
        row = self.current_schedule_row
        self.id = self.sched_dataframe.iloc[row, 0]
        #TODO fix this MESS. it is using the right row and no matter what I get id = 10 back
        print(" editing with ID : " + str(self.sched_dataframe.iloc[3, 0]))
        self.author = self.sched_dataframe.iloc[row, 1]
        self.uri = self.sched_dataframe.iloc[row, 2]
        self.txt = self.sched_dataframe.iloc[row, 3]
        self.sde_queued = self.sched_dataframe.iloc[row, 4]
        self.sde_queued_date_time = self.sched_dataframe.iloc[row, 5]
        self.sde_queued_date_time = self.sde_queued_date_time[: 19]
        sd_input_frame = ctk.CTkFrame(detail_frame)
        sd_id_label = CTkLabel(sd_input_frame, text="ID:")
        sd_id_label.grid(row=0, column=0, padx=1, pady=1)
        sd_id__data = CTkLabel(sd_input_frame, text=self.id)
        sd_id__data.grid(row=0, column=1, padx=1, pady=1)
        sd_author_label = CTkLabel(sd_input_frame, text="Author")
        sd_author_label.grid(row=1, column=0, padx=1, pady=1)
        sd_author_data = CTkLabel(sd_input_frame, text=author)
        sd_author_data.grid(row=1, column=1, padx=1, pady=1)
        sd_uri_label = CTkLabel(sd_input_frame, text="uri:")
        sd_uri_label.grid(row=2, column=0, padx=1, pady=1)
        sd_uri_data = CTkLabel(sd_input_frame, text=self.uri)
        sd_uri_data.grid(row=2, column=1, padx=1, pady=1)
        sd_body_label = CTkLabel(sd_input_frame, text="Body:")
        sd_body_label.grid(row=3, column=0, padx=1, pady=1)
        self.sd_body_data = Text(sd_input_frame, font="Calibri,10,bold", width=40, height=8)
        self.sd_body_data.insert("1.0",self.txt)
        self.sd_body_data.grid(row=3, column=1, padx=1, pady=1)
        sd_input_frame.grid(row=0, column=0)
        #
        sd_queued_panel = ctk.CTkFrame(detail_frame)
        sd_queued_label = CTkLabel(sd_queued_panel, text="Queued:")
        sd_queued_label.pack(side=tk.LEFT)
        self.queued_combo = ttk.Combobox(sd_queued_panel, width=27, values=('True', 'False'), textvariable=self.sde_queued)
        self.queued_combo.set(self.sde_queued)
        self.queued_combo.bind('<<ComboboxSelected>>', self.sel_queued)
        self.queued_combo.pack(side=tk.LEFT)
        sd_queued_panel.grid(row=1, column=0, padx=1, pady=1)
        #
        sd_queued_display_panel = ctk.CTkFrame(detail_frame)
        sd_queued_date_label = CTkLabel(sd_queued_display_panel, text="Date/Time:")
        sd_queued_date_label.pack(side=tk.LEFT)
        self.sd_queued_date_data = CTkLabel(sd_queued_display_panel, text=self.sde_queued_date_time)
        self.sd_queued_date_data.pack(side=tk.LEFT)
        sd_queued_date_show = ctk.CTkButton(sd_queued_display_panel, text='Date/Time Widgets', command=self.time_date_edit_widgets)
        sd_queued_date_show.pack(side=tk.LEFT)
        sd_queued_display_panel.grid(row=2, column=0, padx=1, pady=1)
        sd_n_submit_button = ctk.CTkButton(detail_frame, text='Save Sceduled Task', command=self.save_edited_scheduled_task)
        sd_n_submit_button.grid(row=3, column=0)
        global t_d_p_window # To access the Time/Date widget window outside the function
        self.t_d_p_window= None

    def time_date_edit_widgets(self):
        if self.t_d_p_window is None or not self.t_d_p_window.winfo_exists():
            datetime_object = datetime.datetime.strptime(self.sde_queued_date_time, self.format_string)
            self.t_d_p_window = tkinter.Toplevel()
            self.t_d_p_window.title("Time Selector")
            self.t_d_p_window.geometry("420x230")
            sd_queued_time_panel = ctk.CTkFrame( self.t_d_p_window)
            self.sd_edit_cal = Calendar(sd_queued_time_panel, date_pattern='y-mm-dd', selectmode='day', locale='en_US',
                              cursor="hand1", year=datetime_object.year, month=datetime_object.month, day=datetime_object.day)
            self.sd_edit_cal.grid(row=0, column=0)
            logging.debug("time_date_edit_widgets : " + str(datetime_object.year) + ":" + str(datetime_object.month) + ":" + str(datetime_object.day))
            self.sd_edit_time_picker = SpinTimePicker(sd_queued_time_panel, hour=datetime_object.hour, minute=datetime_object.minute, seconds=datetime_object.second)
            self.sd_edit_time_picker.grid(row=0, column=1, padx=10, pady=10)
            sd_time_picker_button = ctk.CTkButton(sd_queued_time_panel, text='Save Date/Time',
                                               command=self.edit_return_time_date)
            logging.debug("time_date_edit_widgets : " + str(datetime_object.hour) + ":" + str(datetime_object.minute) + ":" + str(datetime_object.second))
            sd_time_picker_button.grid(row=1, column=0)
            sd_queued_time_panel.pack()
            self.t_d_p_window.deiconify()
        else:
            self.t_d_p_window.deiconify()

    def edit_return_time_date(self):
        logging.debug("edit_return_time_date date : " + str(self.sd_edit_cal.get_date()))
        logging.debug("edit_return_time_date time : " + str(self.sd_edit_time_picker.get_time()))
        new_ts = str(self.sd_edit_cal.get_date()) + " " + str(self.sd_edit_time_picker.get_time())
        self.sde_queued_date_time = datetime.datetime.strptime(new_ts, self.format_string)
        logging.debug(" self.sde_queued_date_time date : " + str(self.sde_queued_date_time))
        self.edit_task.queue_datetime = self.sde_queued_date_time
        self.sd_queued_date_data.configure(text=new_ts)
        self.sd_queued_date_data.pack(side=tk.LEFT)
        self.t_d_p_window.withdraw()

    def time_date_new_widgets(self):
        if self.n_t_d_p_window is None or not self.n_t_d_p_window.winfo_exists():
            datetime_object = self.sdn_queued_date_time
            self.n_t_d_p_window = tkinter.Toplevel()
            self.n_t_d_p_window.title("Time Selector")
            self.n_t_d_p_window.geometry("420x230")
            sd_queued_time_panel = ctk.CTkFrame(self.n_t_d_p_window)
            self.sd_new_cal = Calendar(sd_queued_time_panel, date_pattern='y-mm-dd', selectmode='day', locale='en_US',
                              cursor="hand1", year=datetime_object.year, month=datetime_object.month, day=datetime_object.day)
            self.sd_new_cal.grid(row=0, column=0)
            logging.debug("time_date_new_widgets : " + str(datetime_object.year) + ":" + str(datetime_object.month) + ":" + str(datetime_object.day))
            self.sd_new_time_picker = SpinTimePicker(sd_queued_time_panel, hour=datetime_object.hour, minute=datetime_object.minute, seconds=datetime_object.second)
            self.sd_new_time_picker.grid(row=0, column=1, padx=10, pady=10)
            sd_time_picker_button = ctk.CTkButton(sd_queued_time_panel, text='Save Date/Time',
                                                  command=self.new_return_time_date)
            logging.debug("time_date_edit_widgets : " + str(datetime_object.hour) + ":" + str(datetime_object.minute) + ":" + str(datetime_object.second))
            sd_time_picker_button.grid(row=1, column=0)
            sd_queued_time_panel.pack()
            self.n_t_d_p_window.deiconify()
        else:
            self.n_t_d_p_window.deiconify()

    def new_return_time_date(self):
        logging.debug("edit_return_time_date date : " + str(self.sd_new_cal.get_date()))
        logging.debug("new_return_time_date : " + str(self.sd_new_time_picker.get_time()))
        new_ts = str(self.sd_new_cal.get_date()) + " " + str(self.sd_new_time_picker.get_time())
        self.sdn_queued_date_time = datetime.datetime.strptime(new_ts, self.format_string)
        logging.debug(" self.sdn_queued_date_time date : " + str(self.sdn_queued_date_time))
        self.new_task.queue_datetime = self.sdn_queued_date_time
        self.sd_n_queued_date_data.configure(text=new_ts)
        self.sd_n_queued_date_data.pack(side=tk.LEFT)
        self.n_t_d_p_window.withdraw()

    def save_scheduled_task(self):
        self.new_task.txt = self.sd_n_body_data.get("1.0", tk.END)
        logging.debug(" insert_scheduled_post : " + str(self.new_task))
        commit = insert_scheduled_post(self.new_task)
        if commit:
            messagebox.showinfo("Information", "Task was saved successfully")
        else:
            messagebox.showinfo("Information", "Error while saving task")

    def save_edited_scheduled_task(self):
        self.edit_task = PostData(int(self.id), self.author, self.uri, self.sd_body_data.get("1.0", tk.END),
                                  self.sde_queued, self.sde_queued_date_time)
        #self.edit_task.txt = self.sd_body_data.get("1.0", tk.END)
        print("task : " + str(self.edit_task))
        print("que : " + str(self.sde_queued))
        logging.debug(" update_scheduled_post : " + str(self.edit_task))
        commit = update_scheduled_post(self.edit_task)
        if commit:
            messagebox.showinfo("Information", "Task was updated successfully")
        else:
            messagebox.showinfo("Information", "Error while updating task")

    def sel_queued(self, event):
        self.sde_queued = self.queued_combo.get()
        print("queued updated")

    def follower_refresh(self):
        #TODO Refresh is not refreshing the table yet.
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
        logging.debug("clipbaord copied text:" + clip_board_text)

    def clicked(self, event):  # Click event callback function.
        # Probably needs better exception handling, but w/e.
        try:
            clicked = self.pt.get_row_clicked(event)
            self.current_table_row = clicked
        except:
            logging.debug('Error on click event')

    def scheduler_clicked(self, event):  # Click event callback function.
        # Probably needs better exception handling, but w/e.
        logging.debug('Scheduler Window click event')
        try:
            sclicked = self.schedule_table.get_row_clicked(event)
            print("row : ")
            print(str(sclicked))
        except:
            logging.debug('Error on click event')

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
        if no_api == 1:
            filler = []
            filler_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cill."
            filler_uri = "at://did:plc:b8aofukbj2iy00gshmk562iu/app.bsky.feed.post/3lbvimzsix22p"
            filler_date = "2024-11-327T19"
            filler.append({'txt': filler_text, 'time': filler_date, 'uri': filler_uri})
            filler.append({'txt': filler_text, 'time': filler_date, 'uri': filler_uri})
            filler.append({'txt': filler_text, 'time': filler_date, 'uri': filler_uri})
            df = pd.DataFrame(filler, columns=['txt', 'time', 'uri'])
            self.profile = None
        else:
            client_wrapper = ClientWrapper(self.account, self.token)
            self.client = client_wrapper.init_client()
            latest = Driver().perform_get_skeets(self.client)
            self.profile = Driver().get_profile_data(self.client, self.account)
            df = pd.DataFrame(latest, columns=['txt', 'time', 'uri'])
        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    root = Tk()
    app = BlueSkyReader(master=root)
    root.title(app.application_title)
    root.geometry("700x400")
    root.eval('tk::PlaceWindow . center')
    root.clipboard_clear()
    #ctk.set_appearance_mode("dark")
    root.mainloop()




