from threading import Thread

from client import speech2text
from db_operations import connect2db, insert_new_task
from main import get_audio, audio2text, play_sound

ACTIVATION_COMMAND = ["who", "i", "m", "i"]


def save_audio(audio, dest='./temp.wav'):
    """
    :param audio: AudioData
    :param dest: path
    :return: destination path
    """
    with open(dest, mode='bx') as f:
        f.write(audio.get_wav_data())
    return dest


def deal_with_speech():
    sqliteConnection = connect2db("todo_db.db")
    play_sound("todo application is ready")
    while True:
        a = get_audio()
        command = speech2text(save_audio(a), scorer=None, remove_audio=True)

        if all([word in command.lower() for word in ACTIVATION_COMMAND]):
            play_sound("What can I do for you ?")

            task = speech2text(save_audio(get_audio()), scorer=None, remove_audio=True)

            if task:
                if "close" in task.lower():
                    play_sound("I will close")
                    break
                insert_new_task(sqliteConnection, task)
                play_sound("Done")
        else:
            print(command)
    
    sqliteConnection.close()


if __name__ == "__main__":
        
        speach = Thread(target=deal_with_speech)

        speach.start()
        speach.join()
