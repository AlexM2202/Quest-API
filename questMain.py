import customtkinter
import os
import sys
import datetime
import threading
import queue
import lib.questblueAPI as quest
import config.config as config
from tkinter import filedialog
from PIL import ImageTk, Image
from CTkMessagebox import CTkMessagebox

#Global Styles
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")
quest.startLog()

#Scripts
def startEndMon():
    global q_endMon
    q_endMon = queue.Queue()

    quest.logInfo("---STARTING END MONTH SCRIPT---")
    global outPath_endMon
    global start_date_endMon
    global end_date_endMon
    global endMon_size
    quest.init(username.get(), password.get(), key.get())
    quest.startCSV()
    answers = []
    trunks = quest.getTrunkNames()

    local_month_start = endMon_month_start.get()
    local_year_start = endMon_year_start.get()
    local_day_start = endMon_day_start.get()

    local_month_end = endMon_month_end.get()
    local_year_end = endMon_year_end.get()
    local_day_end = endMon_day_end.get()

    start_date_endMon = datetime.date(int(local_year_start), int(local_month_start), int(local_day_start))
    end_date_endMon = datetime.date(int(local_year_end), int(local_month_end), int(local_day_end))
    # num = 1
    for trunk in trunks:
        q_endMon.put(trunk)
        # print(f"(On Trunk {num} of {len(trunks)}) - {round(100*float(num)/float(len(trunks)))}%")
        # progressBar_endMon.set(float(num)/float(len(trunks)))
        # quest.getMonthReport_Trunk(trunk, start_date_endMon, end_date_endMon)
        # num += 1
        # os.system('cls')
    endMon_size = q_endMon.qsize()
    thread_endMon()
    outPath_endMon = quest.closeCSV()
    output_path_endMon.configure(text=f"{outPath_endMon}")
    output_path_endMon.update()
    open_csv_folder_endMon.grid(column=3, row=7, padx=10, pady=12,columnspan=2)
    quest.logInfo("---ENDING END MONTH SCRIPT---")
    return

def startTF():
    quest.logInfo("---STARTING TOLL FREE SCRIPT---")
    global outPath_TF
    global q_TF
    global tf_start_date
    global tf_end_date
    global tf_size

    q_TF = queue.Queue()

    quest.init(username.get(), password.get(), key.get())
    quest.startCSV()
    dids = [800, 833, 844, 855, 866, 877, 888]
    
    local_month_start = tf_month_start.get()
    local_year_start = tf_year_start.get()
    local_day_start = tf_day_start.get()

    local_month_end = tf_month_end.get()
    local_year_end = tf_year_end.get()
    local_day_end = tf_day_end.get()

    tf_start_date = datetime.date(int(local_year_start), int(local_month_start), int(local_day_start))
    tf_end_date = datetime.date(int(local_year_end), int(local_month_end), int(local_day_end))

    # num =1

    for did in dids:
        q_TF.put(did)
        # progressBar_TF.set(float(num)/float(len(dids)))
        # quest.tollFreeMonth(did, date_start, date_end) # type: ignore
        # num += 1
    tf_size = q_TF.qsize()
    thread_TF()
    outPath_TF = quest.closeCSV()
    output_path_TF.configure(text=f"{outPath_TF}")
    output_path_TF.update()
    open_csv_folder_TF.grid(column=3, row=7, padx=10, pady=12,columnspan=2)
    quest.logInfo("---ENDING TOLL FREE SCRIPT---")
    return

def worker_endMon():
    while not q_endMon.empty():
        trunk = q_endMon.get()
        done = endMon_size - q_endMon.qsize()
        progressBar_endMon.set(float(done)/float(endMon_size))
        quest.getMonthReport_Trunk(trunk, start_date_endMon, end_date_endMon)

def thread_endMon():
    thread_list = []
    if config.max_thread == True:
        max_threads = config.thread_limit
    elif config.max_thread == False:
        max_threads = q_endMon.qsize()
    for t in range(max_threads):
        thread = threading.Thread(target=worker_endMon)
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()

def worker_TF():
    while not q_TF.empty():
        did = q_TF.get()
        done = tf_size - q_TF.qsize()
        progressBar_TF.set(float(done)/float(tf_size))
        quest.tollFreeMonth(did, tf_start_date, tf_end_date)

def thread_TF():
    thread_list = []
    if config.max_thread == True:
        max_threads = config.thread_limit
    elif config.max_thread == False:
        max_threads = q_TF.qsize()
    for t in range(max_threads):
        thread = threading.Thread(target=worker_TF)
        thread_list.append(thread)
    
    for thread in thread_list:
        thread.start()
    
    for thread in thread_list:
        thread.join()

#Pages
def Login(root):
    
    global username
    global password
    global key

    global checkRemember
    global fileExists
    username = customtkinter.StringVar()
    password = customtkinter.StringVar()
    key = customtkinter.StringVar()
    checkRemember = customtkinter.IntVar()
    try:
        with open('./lib/temp/login.tmp', 'r+') as rememberFile:
            fileExists = True
            line = rememberFile.readline()
            checkRemember = line.strip()
            if int(checkRemember) == 1:
                line = rememberFile.readline()
                username.set(line.strip())
                line = rememberFile.readline()
                password.set(line.strip())
                line = rememberFile.readline()
                key.set(line.strip())
                
                checkRemember = customtkinter.IntVar(value=int(checkRemember))
        rememberFile.close()
        # os.remove('./lib/temp/login.tmp')
    except:
        fileExists = False
        quest.logInfo("NO Remember Me file")

    page = customtkinter.CTkFrame(root)

    greeting = customtkinter.CTkLabel(master=page, text="Welcome!", font=("Roboto", 18))
    username_label = customtkinter.CTkLabel(master=page, text="Username", font=("Roboto", 12))
    username_entry = customtkinter.CTkEntry(master=page, textvariable=username)
    password_label = customtkinter.CTkLabel(master=page, text="Password", font=("Roboto", 12))
    password_entry = customtkinter.CTkEntry(master=page, show="*", textvariable=password)
    key_label = customtkinter.CTkLabel(master=page, text="API Key", font=("Roboto", 12))
    key_entry = customtkinter.CTkEntry(master=page, textvariable=key)
    login_button = customtkinter.CTkButton(master=page, text="Login", command=check_Login_filled)
    remember_me_box = customtkinter.CTkCheckBox(master=page, text="Remember Me", variable=checkRemember)
    version = customtkinter.CTkLabel(master=root, text="v1.3", font=("Roboto", 12))

    page.grid(column=0, row=0, padx=60, pady=20, sticky="nsew")
    greeting.grid(column=0, row=0, columnspan=3, padx=10, pady=12)
    username_label.grid(column=0, row=1, padx=10, pady=12)
    username_entry.grid(column=1, row=1, columnspan=2, padx=10, pady=12)
    password_label.grid(column=0,row=2, padx=10, pady=12)
    password_entry.grid(column=1, row=2, columnspan=2, padx=10, pady=12)
    key_label.grid(column=0, row=3, padx=10, pady=12)
    key_entry.grid(column=1, row=3, columnspan=2, padx=10, pady=12)
    login_button.grid(column=0, row=4, columnspan=3, padx=10, pady=12)
    remember_me_box.grid(column=0, row=5, columnspan=3, padx=10, pady=12)
    version.grid(column=0, row=1)
    quest.logInfo("Displayed Login Page")
    

def menu(root):
    quest.logInfo(f"Login seccessful! User - {username.get()} Password - {password.get()} Key - {key.get()}")
    page = customtkinter.CTkFrame(root)

    imgFrame = customtkinter.CTkFrame(master=page, width=100, height=100)
    img = customtkinter.CTkImage(Image.open(find_by_relative_path("lib" + os.sep + "assets" + os.sep + "HD-TEC-Logo.png")), size=(100,100))
    img_label = customtkinter.CTkLabel(master=imgFrame, text="", image=img)

    tf_label = customtkinter.CTkLabel(master=page, text="Toll Free", font=("Roboto", 14))
    tf_button = customtkinter.CTkButton(master=page, text="Select", font=("Roboto", 12), command=change_tf)

    endMon_label = customtkinter.CTkLabel(master=page, text="End Of Month", font=("Roboto", 14))
    endMon_button = customtkinter.CTkButton(master=page, text="Select", font=("Roboto", 12), command=change_endMon)

    back_button = customtkinter.CTkButton(master=page, text="Back", font=("Roboto", 12), command=change_login)
    version = customtkinter.CTkLabel(master=root, text="v1.3", font=("Roboto", 12))

    page.grid(column=0, row=0, padx=60, pady=20)
    version.grid(column=0, row=1)
    imgFrame.grid(column=0, row=0, columnspan=3, rowspan=2, padx=60, pady=20)
    img_label.grid(column=0, row=0, columnspan=3, rowspan=2)

    tf_label.grid(column=0, row=2)
    tf_button.grid(column=0, row=3, padx=10, pady=12)
    endMon_label.grid(column=2, row=2)
    endMon_button.grid(column=2, row=3, padx=10, pady=12)
    back_button.grid(column=1, row=5, padx=10, pady=30)
    quest.logInfo("Displayed Menu")


def endMon(root):
    global endMon_day_start
    global endMon_month_start
    global endMon_year_start

    global endMon_day_end
    global endMon_month_end
    global endMon_year_end

    global output_path_endMon
    global progressBar_endMon
    global open_csv_folder_endMon

    months = ["1","2","3","4","5","6","7","8","9","10","11","12"]
    endMon_day_start = customtkinter.StringVar()
    endMon_month_start = customtkinter.StringVar(root)
    endMon_year_start = customtkinter.StringVar()
    endMon_day_end = customtkinter.StringVar()
    endMon_month_end = customtkinter.StringVar(root)
    endMon_year_end = customtkinter.StringVar()
    
    page = customtkinter.CTkFrame(root)
    startGroup = customtkinter.CTkFrame(page)
    endGroup = customtkinter.CTkFrame(page)
    label = customtkinter.CTkLabel(master=page, text="End Month Script", font=("Roboto", 18))
    start_label = customtkinter.CTkLabel(master=startGroup, text="Start Date", font=("Roboto",14))
    end_label = customtkinter.CTkLabel(master=endGroup, text="End Date", font=("Roboto",14))
    start_sel_month_label = customtkinter.CTkLabel(master=startGroup, text="Select Month", font=("Roboto", 12))
    start_select_month_box= customtkinter.CTkOptionMenu(master=startGroup, variable=endMon_month_start, values=months)
    start_day_label = customtkinter.CTkLabel(master=startGroup, text="Day", font=("Roboto", 12))
    start_day_entry = customtkinter.CTkEntry(master=startGroup, textvariable=endMon_day_start)
    start_year_label = customtkinter.CTkLabel(master=startGroup, text="Enter Year", font=("Roboto", 12))
    start_year_entry = customtkinter.CTkEntry(master=startGroup, textvariable=endMon_year_start)
    end_sel_month_label = customtkinter.CTkLabel(master=endGroup, text="Select Month", font=("Roboto", 12))
    end_select_month_box= customtkinter.CTkOptionMenu(master=endGroup, variable=endMon_month_end, values=months)
    end_day_label = customtkinter.CTkLabel(master=endGroup, text="Day", font=("Roboto", 12))
    end_day_entry = customtkinter.CTkEntry(master=endGroup, textvariable=endMon_day_end)
    end_year_label = customtkinter.CTkLabel(master=endGroup, text="Enter Year", font=("Roboto", 12))
    end_year_entry = customtkinter.CTkEntry(master=endGroup, textvariable=endMon_year_end)
    back_button = customtkinter.CTkButton(master=page, text="Back", font=("Roboto", 12), command=change_menu)
    start_button = customtkinter.CTkButton(master=page, text="Start", font=("Roboto", 12), command=startEndMonThread)
    output_path_endMon = customtkinter.CTkLabel(master=page, text="", font=("Roboto", 11))
    progressBar_endMon = customtkinter.CTkProgressBar(master=page, width=500)
    open_csv_folder_endMon = customtkinter.CTkButton(master=page, text="Open", font=("Roboto", 12), command=open_file_endMon)
    progressBar_endMon.set(0)

    page.grid(column=0, row=0, padx=60, pady=20)
    label.grid(column=1, row=0, columnspan=2, padx=10, pady=12)

    start_label.grid(column=0, row=0, columnspan=2, padx=10, pady=12)
    start_sel_month_label.grid(column=0, row=1, padx=10, pady=12)
    start_select_month_box.grid(column=1, row=1, padx=10, pady=12)
    start_day_label.grid(column=0, row=2, padx=10, pady=12)
    start_day_entry.grid(column=1, row=2, padx=10, pady=12)
    start_year_label.grid(column=0, row=3, padx=10, pady=12)
    start_year_entry.grid(column=1, row=3, padx=10, pady=12)

    end_label.grid(column=0, row=0, columnspan=2, padx=10, pady=12)
    end_sel_month_label.grid(column=0, row=1, padx=10, pady=12)
    end_select_month_box.grid(column=1, row=1, padx=10, pady=12)
    end_day_label.grid(column=0, row=2, padx=10, pady=12)
    end_day_entry.grid(column=1, row=2, padx=10, pady=12)
    end_year_label.grid(column=0, row=3, padx=10, pady=12)
    end_year_entry.grid(column=1, row=3, padx=10, pady=12)

    startGroup.grid(column=0, row=2, padx=60, pady=20, columnspan=2, rowspan=3)
    endGroup.grid(column=2, row=2, padx=60, pady=20, columnspan=2, rowspan=3)


    back_button.grid(column=0, row=5, columnspan=2, padx=10, pady=12)
    start_button.grid(column=2, row=5, columnspan=2, padx=10, pady=12)
    progressBar_endMon.grid(column=0, row=6, padx=10, pady=12,columnspan=5)
    output_path_endMon.grid(column=0, row=7, padx=10, pady=12,columnspan=3)
    # open_csv_folder_endMon.grid(column=3, row=7, padx=10, pady=12,columnspan=2)
    open_csv_folder_endMon.grid_remove()
    quest.logInfo("Displayed EndMon Page")

def tf_page(root):
    global tf_day_start
    global tf_month_start
    global tf_year_start

    global tf_day_end
    global tf_month_end
    global tf_year_end

    global output_path_TF
    global progressBar_TF
    global open_csv_folder_TF
    
    months = ["1","2","3","4","5","6","7","8","9","10","11","12"]
    tf_day_start = customtkinter.StringVar()
    tf_month_start = customtkinter.StringVar(root)
    tf_year_start = customtkinter.StringVar()
    tf_day_end = customtkinter.StringVar()
    tf_month_end = customtkinter.StringVar(root)
    tf_year_end = customtkinter.StringVar()
    
    page = customtkinter.CTkFrame(root)
    startGroup = customtkinter.CTkFrame(page)
    endGroup = customtkinter.CTkFrame(page)
    label = customtkinter.CTkLabel(master=page, text="Toll Free Script", font=("Roboto", 18))
    start_label = customtkinter.CTkLabel(master=startGroup, text="Start Date", font=("Roboto",14))
    end_label = customtkinter.CTkLabel(master=endGroup, text="End Date", font=("Roboto",14))
    start_sel_month_label = customtkinter.CTkLabel(master=startGroup, text="Select Month", font=("Roboto", 12))
    start_select_month_box= customtkinter.CTkOptionMenu(master=startGroup, variable=tf_month_start, values=months)
    start_day_label = customtkinter.CTkLabel(master=startGroup, text="Day", font=("Roboto", 12))
    start_day_entry = customtkinter.CTkEntry(master=startGroup, textvariable=tf_day_start)
    start_year_label = customtkinter.CTkLabel(master=startGroup, text="Enter Year", font=("Roboto", 12))
    start_year_entry = customtkinter.CTkEntry(master=startGroup, textvariable=tf_year_start)
    end_sel_month_label = customtkinter.CTkLabel(master=endGroup, text="Select Month", font=("Roboto", 12))
    end_select_month_box= customtkinter.CTkOptionMenu(master=endGroup, variable=tf_month_end, values=months)
    end_day_label = customtkinter.CTkLabel(master=endGroup, text="Day", font=("Roboto", 12))
    end_day_entry = customtkinter.CTkEntry(master=endGroup, textvariable=tf_day_end)
    end_year_label = customtkinter.CTkLabel(master=endGroup, text="Enter Year", font=("Roboto", 12))
    end_year_entry = customtkinter.CTkEntry(master=endGroup, textvariable=tf_year_end)
    back_button = customtkinter.CTkButton(master=page, text="Back", font=("Roboto", 12), command=change_menu)
    start_button = customtkinter.CTkButton(master=page, text="Start", font=("Roboto", 12), command=startTfThread)
    output_path_TF = customtkinter.CTkLabel(master=page, text="", font=("Roboto", 11))
    progressBar_TF = customtkinter.CTkProgressBar(master=page, width=500)
    open_csv_folder_TF = customtkinter.CTkButton(master=page, text="Open", font=("Roboto", 12), command=open_file_tf)

    progressBar_TF.set(0)

    page.grid(column=0, row=0, padx=60, pady=20)
    label.grid(column=0, row=0, columnspan=4, padx=10, pady=12)

    start_label.grid(column=0, row=0, columnspan=2, padx=10, pady=12)
    start_sel_month_label.grid(column=0, row=1, padx=10, pady=12)
    start_select_month_box.grid(column=1, row=1, padx=10, pady=12)
    start_day_label.grid(column=0, row=2, padx=10, pady=12)
    start_day_entry.grid(column=1, row=2, padx=10, pady=12)
    start_year_label.grid(column=0, row=3, padx=10, pady=12)
    start_year_entry.grid(column=1, row=3, padx=10, pady=12)

    end_label.grid(column=0, row=0, columnspan=2, padx=10, pady=12)
    end_sel_month_label.grid(column=0, row=1, padx=10, pady=12)
    end_select_month_box.grid(column=1, row=1, padx=10, pady=12)
    end_day_label.grid(column=0, row=2, padx=10, pady=12)
    end_day_entry.grid(column=1, row=2, padx=10, pady=12)
    end_year_label.grid(column=0, row=3, padx=10, pady=12)
    end_year_entry.grid(column=1, row=3, padx=10, pady=12)

    startGroup.grid(column=0, row=2, padx=60, pady=20, columnspan=2, rowspan=3)
    endGroup.grid(column=2, row=2, padx=60, pady=20, columnspan=2, rowspan=3)


    back_button.grid(column=0, row=5, columnspan=2, padx=10, pady=12)
    start_button.grid(column=2, row=5, columnspan=2, padx=10, pady=12)
    progressBar_TF.grid(column=0, row=6,  padx=10, pady=12,columnspan=5)
    output_path_TF.grid(column=0, row=7,  padx=10, pady=12,columnspan=3)
    # open_csv_folder_TF.grid(column=3, row=7, padx=10, pady=12,columnspan=2)
    open_csv_folder_TF.grid_remove()
    quest.logInfo("Displayed Toll Free Page")

#Functions
def change_login():
    quest.logInfo("Go to Login")
    global root
    for widget in root.winfo_children():
        widget.destroy()
    Login(root)

def change_tf():
    quest.logInfo("Go to Toll Free")
    global root
    for widget in root.winfo_children():
        widget.destroy()
    tf_page(root)

def change_endMon():
    quest.logInfo("Go to EndMon")
    global root
    for widget in root.winfo_children():
        widget.destroy()
    endMon(root)

def change_menu():
    quest.logInfo("Go to Menu")
    global root
    for widget in root.winfo_children():
        widget.destroy()
    menu(root)

def check_Login_filled():
    quest.logInfo("Attempt Login")
    global root

    usernameGot = username.get()
    passwordGot = password.get()
    keyGot = key.get()
    if config.debug == False:
        if usernameGot == '' or passwordGot == '' or keyGot == '':
            CTkMessagebox(title="Error", message="Not all fields were filled!", icon="cancel")
        else:
            quest.init(usernameGot, passwordGot, keyGot)
            response = quest.check_creds()
            if str(response) == "<Response [401]>":
                quest.logInfo("INVALID LOGIN")
                CTkMessagebox(title="Invalid Login", message="Invalid login credentials!", icon="cancel")
            else:
                if checkRemember.get() == 1 and fileExists == False:
                    writeRememberMe()
                else:
                    if fileExists == True and checkRemember.get() == 1:
                        writeRememberMe()
                    else:
                        try:
                            os.remove('./lib/temp/login.tmp')
                        except:
                            quest.logInfo("No Remember Me File")
                change_menu()
    if config.debug == True:
        change_menu()

def on_quit():
    quest.logInfo("ARE YOU SURE YOU WANT TO QUIT?")
    global root
    msg = CTkMessagebox(title="Quit?", message="Do you wnat to quit the program?", icon="question", option_1="No", option_2="Yes")
    response = msg.get()

    if response == "Yes":
        quest.logInfo("QUITTING!")
        root.destroy()
    else:
        return
    
def startEndMonThread():
    if config.debug == False:
        if endMon_month_start.get() == '':
            quest.logInfo("INVALID DATE - missing start_month")
            CTkMessagebox(title="Invalid Date", message=f"Missing start date month!", icon="cancel")
        elif endMon_month_end.get() == '':
            quest.logInfo("INVALID DATE - missing end_month")
            CTkMessagebox(title="Invalid Date", message=f"Missing end date month!", icon="cancel")
        elif endMon_day_start.get() == '':
            quest.logInfo("INVALID DATE - missing start_day")
            CTkMessagebox(title="Invalid Date", message=f"Missing start date day!", icon="cancel")
        elif endMon_day_end.get() == '':
            quest.logInfo("INVALID DATE - missing end_day")
            CTkMessagebox(title="Invalid Date", message=f"Missing end date day!", icon="cancel")
        elif endMon_year_start.get() == '':
            quest.logInfo("INVALID DATE - missing start_year")
            CTkMessagebox(title="Invalid Date", message=f"Missing start date year!", icon="cancel")
        elif endMon_year_end.get() == '':
            quest.logInfo("INVALID DATE - missing end_year")
            CTkMessagebox(title="Invalid Date", message=f"Missing end date year!", icon="cancel")
        elif int(endMon_month_end.get()) < int(endMon_month_start.get()) and int(endMon_year_end.get()) <= int(endMon_year_start.get()):
            quest.logInfo("INVALID DATE - MONTH DATE RANGE")
            CTkMessagebox(title="Invalid Date", message=f"Not a valid date range!\nEnd date month is before start date month!", icon="cancel")
        elif int(endMon_day_start.get()) == int(endMon_day_end.get()) and int(endMon_month_start.get()) == int(endMon_month_end.get()) and int(endMon_year_start.get()) == int(endMon_year_end.get()):
            quest.logInfo("INVALID DATE - SAME DAY")
            CTkMessagebox(title="Invalid Date", message=f"Not a valid date range!\nStart and end date are the same!", icon="cancel")
        elif int(endMon_year_end.get()) < int(endMon_year_start.get()):
            quest.logInfo("INVALID DATE - end_year < start_year")
            CTkMessagebox(title="Invalid Date", message=f"Not a valid date range!\nStart year > end year", icon="cancel")
        else:
            quest.logInfo("STARTING NEW THREAD")
            thread = threading.Thread(target=startEndMon)
            thread.start()
    else:
        CTkMessagebox(title="DEBUG", message=f"Scripts can't be run in debugging mode!", icon="cancel")

def startTfThread():
    if config.debug == False:
        if tf_month_start.get() == '':
            quest.logInfo("INVALID DATE - missing start_month")
            CTkMessagebox(title="Invalid Date", message=f"Missing start date month!", icon="cancel")
        elif tf_month_end.get() == '':
            quest.logInfo("INVALID DATE - missing end_month")
            CTkMessagebox(title="Invalid Date", message=f"Missing end date month!", icon="cancel")
        elif tf_day_start.get() == '':
            quest.logInfo("INVALID DATE - missing start_day")
            CTkMessagebox(title="Invalid Date", message=f"Missing start date day!", icon="cancel")
        elif tf_day_end.get() == '':
            quest.logInfo("INVALID DATE - missing end_day")
            CTkMessagebox(title="Invalid Date", message=f"Missing end date day!", icon="cancel")
        elif tf_year_start.get() == '':
            quest.logInfo("INVALID DATE - missing start_year")
            CTkMessagebox(title="Invalid Date", message=f"Missing start date year!", icon="cancel")
        elif tf_year_end.get() == '':
            quest.logInfo("INVALID DATE - missing end_year")
            CTkMessagebox(title="Invalid Date", message=f"Missing end date year!", icon="cancel")
        elif int(tf_month_end.get()) < int(tf_month_start.get()) and int(tf_year_end.get()) <= int(tf_year_start.get()):
            quest.logInfo("INVALID DATE - MONTH DATE RANGE")
            CTkMessagebox(title="Invalid Date", message=f"Not a valid date range!\nEnd date month is before start date month!", icon="cancel")
        elif int(tf_day_start.get()) == int(tf_day_end.get()) and int(tf_month_start.get()) == int(tf_month_end.get()) and int(tf_year_start.get()) == int(tf_year_end.get()):
            quest.logInfo("INVALID DATE - SAME DAY")
            CTkMessagebox(title="Invalid Date", message=f"Not a valid date range!\nStart and end date are the same!", icon="cancel")
        elif int(tf_year_end.get()) < int(tf_year_start.get()):
            quest.logInfo("INVALID DATE - end_year < start_year")
            CTkMessagebox(title="Invalid Date", message=f"Not a valid date range!\nStart year > end year", icon="cancel")
        else:
            quest.logInfo("STARTING NEW THREAD")
            thread = threading.Thread(target=startTF)
            thread.start()
    else:
        CTkMessagebox(title="DEBUG", message=f"Scripts can't be run in debugging mode!", icon="cancel")


def find_by_relative_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def open_file_endMon():
    global root
    global outPath_endMon
    # root = tkinter.Tk()
    tempPath = str(outPath_endMon)
    head, tail = os.path.split(str(tempPath))
    quest.logInfo("Attempt open file")
    return filedialog.askopenfilename(initialdir=head)
    
def writeRememberMe():
    with open('./lib/temp/login.tmp', 'w') as read:
        read.write('1' + '\n')
        read.write(username.get() + '\n')
        read.write(password.get() + '\n')
        read.write(key.get() + '\n')
    read.close()

def open_file_tf():
    global root
    global outPath_TF
    # root = tkinter.Tk()
    tempPath = str(outPath_TF)
    head, tail = os.path.split(str(tempPath))
    quest.logInfo("Attempt open file")
    return filedialog.askopenfilename(initialdir=head)

def main():
    global root
    root = customtkinter.CTk()
    root.title("QuestBlue Reports")

    root.iconbitmap(find_by_relative_path(("lib" + os.sep + "assets" + os.sep + "hdtecIcon.ico")))
    Login(root)
    root.protocol("WM_DELETE_WINDOW", on_quit)
    root.mainloop()
    quest.closeLog()

if __name__ == "__main__":
    main()