import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from db_operations import (
    connect2db,
    get_all_tasks,
    insert_new_task)
from PIL import Image, ImageTk
import threading
import os
from dotenv import load_dotenv
import logging
from utility import *
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone

load_dotenv()


class TodoAppGUI:
    def __init__(self, master, deepgram, db_conn):
        self.master = master
        self.deepgram = deepgram
        self.db_conn = db_conn
        self.master.title("ToDo List: Don't Be Lasy")
        # root.iconbitmap('/home/mohamed/Pictures/1024px-GNOME_Todo_icon_2019.svg.png')
        self.master.geometry("800x500")
        app_frame = tk.Frame(self.master)
        app_frame.pack(pady=10)

        # Define our Font
        list_font = Font(
            family="Verdana",
            size=15,
            weight="normal"
        )

        # Add Buttons Frame
        self.buttons_frame = tk.Frame(self.master)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_button = tk.Button(self.buttons_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.buttons_frame, text="Delete Task", command=self.delete_selected_task)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.refresh_button = tk.Button(self.buttons_frame, text="Refresh", command=self.refresh_tasks)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.microphone_button = tk.Button(self.buttons_frame, text="Microphone", command=self.toggle_listening)
        self.microphone_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Add Tasks Table Frame
        self.tasks_frame = tk.Frame(self.master)
        self.tasks_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.tasks_table = ttk.Treeview(self.tasks_frame, columns=("ID", "Task"), selectmode="browse")
        self.tasks_table.heading("#0", text="ID")
        self.tasks_table.column("#0", width=50, anchor="center")
        # self.tasks_table.heading("ID", text="ID")
        # self.tasks_table.column("ID", width=100, anchor="center")
        self.tasks_table.heading("Task", text="Task")
        self.tasks_table.column("Task", width=600)
        self.tasks_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tasks_scrollbar = ttk.Scrollbar(self.tasks_frame, orient="vertical", command=self.tasks_table.yview)
        self.tasks_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.tasks_table.configure(yscrollcommand=self.tasks_scrollbar.set)

        self.populate_tasks_table()

        self.is_listening = False
        self.text = ""

    def add_task(self):
        # You can implement this method to add a task to the database
        pass

    def delete_selected_task(self):
        # You can implement this method to delete the selected task from the database
        pass

    def refresh_tasks(self):
        # You can implement this method to refresh the tasks in the table
        pass

    def populate_tasks_table(self):
        # Populate tasks table from database
        tasks = get_all_tasks(self.db_conn)
        for task in tasks:
            self.tasks_table.insert("", "end", values=task)

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        self.is_listening = True
        self.microphone_button.config(state="disabled")
        threading.Thread(target=self.listen).start()

    def on_message(self, result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if len(sentence) == 0:
            return
        self.text += f"{sentence}\n"

    def listen(self):
        try:
            # New connection
            dg_connection = self.dg_connection()

            # Open a microphone stream on the default input device
            microphone = Microphone(dg_connection.send)

            # start microphone
            microphone.start()

            # This will block until the window is closed
            self.master.mainloop()

            # Wait for the microphone to close
            microphone.finish()

            # Indicate that we've finished
            dg_connection.finish()

        except Exception as e:
            print(f"Could not open socket: {e}")
            return

    def stop_listening(self):
        self.is_listening = False
        self.microphone_button.config(state="enabled")
        insert_new_task(self.db_conn, self.text)

    def dg_connection(self):
        connection = self.deepgram.listen.live.v("1")
        connection.on(
            LiveTranscriptionEvents.Transcript,
            self.on_message)
        options: LiveOptions = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            # To get UtteranceEnd, the following must be set:
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
        )
        connection.start(options)
        return connection


class TodoApp:

    def deepgram_client(self):
        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
        config = DeepgramClientOptions(
            verbose=logging.WARNING,
            options={"keepalive": "true"})
        return DeepgramClient(
            api_key=os.getenv("DEEPGRAM_API"),
            config=config)

    def __init__(self, master):
        self.sqlite_connection = connect2db("todo_db.db")
        self.deepgram = self.deepgram_client()
        self.master = master

        self.app = TodoAppGUI(
            master=master,
            db_conn=self.sqlite_connection,
            deepgram=self.deepgram)


def main():
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
