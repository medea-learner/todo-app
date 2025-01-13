from tkinter import *
from tkinter.font import Font
from db_operations import connect2db, get_all_tasks
from utility import *

sqliteConnection = connect2db("todo_db.db")
root = Tk()
root.title("ToDo List: Don't Be Lasy")
#root.iconbitmap('/home/mohamed/Pictures/1024px-GNOME_Todo_icon_2019.svg.png')
root.geometry("800x500")

app_frame = Frame(root)
app_frame.pack(pady=10)

# Define our Font
list_font = Font(
    family="Verdana",
    size=15,
    weight="normal"
)

# Create list box
todo_list = Listbox(
    app_frame, 
    font=list_font,
    width=60,
    height=15,
    #bg="SystemButtonFace", 
    bd=0, 
    fg="#464646",
    highlightthickness=0.5,
    selectbackground="#a6a6a6",
    activestyle=None
)
todo_list.pack(side=LEFT, fill=BOTH)

# load todo list
tasks = get_all_tasks(sqliteConnection)
for i, task in enumerate(tasks):
    todo_list.insert(END, str(i) + "- " + '...   CREATED AT '.join(task))

tasks_scrollbar = Scrollbar(app_frame)
tasks_scrollbar.pack(side=RIGHT, fill=BOTH)

# Add scrollbar to todolist
todo_list.config(yscrollcommand=tasks_scrollbar.set)
tasks_scrollbar.config(command=todo_list.yview)

# Create a button frame
btn_frame = Frame(root)
btn_frame.pack(pady=20)

# Refresh button
refresh_btn = Button(btn_frame, text="Refresh", command=lambda: refresh(sqliteConnection, todo_list))

# Cross off button
cross_off_btn = Button(btn_frame, text="Cross off", command=cross_off)

# Delete button
delete_btn = Button(btn_frame, text="Delete", command=lambda: delete(todo_list))

# Clear List button
clear_btn = Button(btn_frame, text="Clear List", command=clear)

refresh_btn.grid(row=0, column=0)
cross_off_btn.grid(row=0, column=1, padx=20)
delete_btn.grid(row=0, column=2)
clear_btn.grid(row=0, column=3, padx=20)


#def start_app():
root.mainloop()
