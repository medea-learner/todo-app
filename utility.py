import tkinter as tk

# Refresh button
from db_operations import get_all_tasks


def refresh_tasks(conn, todo_list):
    tasks = get_all_tasks(conn)
    for i, task in enumerate(tasks):
        try:
            todo_list.delete(i)
        except:
            pass
        finally:
            todo_list.insert(i, str(i) + "- " + '...   CREATED AT '.join(task))


# Cross off button
def cross_off():
    pass


# Delete button
def delete_task(todo_list):
    todo_list.delete(tk.ANCHOR)


# Clear List button
def clear_tasks():
    pass
