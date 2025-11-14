# AllTools.py
import pyautogui as pag, time, os, json, glob, subprocess, sys, sqlite3, psutil, dateparser, threading, wikipediaapi, firebase_admin, tkinter as tk, requests
from datetime import datetime, timedelta, date
from tkcalendar import Calendar
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from plyer import notification
from firebase_admin import credentials, messaging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import notifier

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.environ["SERVICE_ACCOUNT_PATH"])
firebase_admin.initialize_app(cred)

# Read FCM token from file
with open(os.environ["FCM_TOKEN_PATH"]) as f:
    fcm_token = f.read().strip()

todo_file = "memory/todos.json"
if not os.path.exists(todo_file):
    with open(todo_file, "w") as f:
        json.dump([], f)

history_file = "memory/full_history.json"
if not os.path.exists(history_file):
    with open(history_file, "w") as f:
        json.dump({}, f)

convo_file = "memory/conversation_window.json"
if not os.path.exists(convo_file):
    with open(convo_file, "w") as f:
        json.dump([], f)

class KnowledgeManager:
    def __init__(self):
        self.knowledge_path = "knowledge.py"

    def insert_location(self, text,keyword = "location = ["):
        with open(self.knowledge_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if keyword in line:
                insert_line = i + 1
                lines.insert(insert_line, text + ("\n" if not text.endswith("\n") else ""))
                break
        else:
            print(f"⚠️ Keyword '{keyword}' not found in '{self.knowledge_path}'.")
            return
        with open(self.knowledge_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✅ Inserted text after keyword '{keyword}' in '{self.knowledge_path}'.")


class BasicTools:
    def __init__(self):
        self.app_name = None
        self.path = None
        self.file_name = None
    
    def open_app(self, app_name):
        try:
            self.app_name = app_name

            # Define aliases for app names to process names
            process_aliases = {
                "google chrome": "chrome.exe",
                "chrome": "chrome.exe",
                "opera": "opera.exe",
                "spotify": "spotify.exe",
                "visual studio code": "code.exe",
                "vscode": "code.exe",
                "notepad": "notepad.exe",
                "file explorer": "explorer.exe"
            }

            # Normalize process name
            app_key = app_name.lower()
            process_name = process_aliases.get(app_key, app_key + ".exe")

            # Check if the app is already running
            is_running = any(process_name.lower() == proc.name().lower() for proc in psutil.process_iter())
            if is_running:
                print("[INFO] Launch cancelled, app already running.")
                return "app already open"

            before = [p.name() for p in psutil.process_iter()]

            # Launch using Start Menu
            pag.hotkey('win', 's')
            time.sleep(1)
            for i in self.app_name:
                pag.press(i)
            time.sleep(1)
            pag.press('enter')

            print("[INFO] Waiting for app to launch...")
            time.sleep(5)

            after = [p.name() for p in psutil.process_iter()]
            print(f"[INFO] Launched processes: {list(set(after) - set(before))}")

            target = process_name.lower().replace(".exe", "")
            if any(target in proc.lower() for proc in after):
                print(f"[SUCCESS] '{self.app_name}' opened successfully.")
                return "opened"
            else:
                print(f"[FAILURE] '{self.app_name}' did not appear in running processes.")
                return "error occured - app not opened"

        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            return f"error occured {e}"



    def open_app_with_path(self, path):
        if os.path.exists(path):
            print(f"File exists, launching {self.app_name}...")
            try:
                os.startfile(path)
            except Exception as e:
                print(f"Failed to launch {self.app_name}: {e}")
        else:
            print(f"Path does not exist: {path}")

    
    def set_volume(self, level):  # level between 0.0 and 1.0
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level, None)
            return "changed"
        except Exception as e:
            print(f"Failed to set volume: {e}")
            return f"error occured {e}"

    def search_for_files(self, file_name):
        self.file_name = file_name
        os.system("explorer shell:MyComputerFolder")
        time.sleep(2)
        pag.hotkey('ctrl', 'f')
        time.sleep(1)
        pag.write(self.file_name, interval=0.05)
        pag.press('enter')
        time.sleep(2)
    
    def make_any(self, name, loc, type):
        if type == "folder":
            os.makedirs(os.path.join(loc, name), exist_ok=True)
        elif type == "text file":
            with open(os.path.join(loc, f"{name}.txt"), 'w') as f:
                f.write("")

    def shutdown_system(self):
            os.system("shutdown /s /t 10")
            self.start_timer(10, "Shutting down...")

    def restart_system(self):
            os.system("shutdown /r /t 10")
            self.start_timer(10, "Restarting...")
    
    def lock_system(self):
        os.system("rundll32.exe user32.dll,LockWorkStation")

    def start_timer(self, duration, message=""):
        try:
            if "minutes" in duration:
                dur = int(duration.replace("minutes", "").strip()) * 60
            elif "hours" in duration:
                dur = int(duration.replace("hours", "").strip()) * 3600
            elif "seconds" in duration:
                dur = int(duration.replace("seconds", "").strip())
            else:
                dur = int(duration)  # assume raw number is seconds

            def update():
                nonlocal dur
                if dur >= 0:
                    hrs, rem = divmod(dur, 3600)
                    mins, secs = divmod(rem, 60)
                    label.config(text=f"{hrs:02}:{mins:02}:{secs:02}")
                    dur -= 1
                    root.after(1000, update)
                else:
                    label.config(text=f"{message if message != 'none' else 'Time is up!'}")
                    root.after(1500, lambda: (root.destroy(), sys.exit()))  # close + exit

            root = tk.Tk()
            root.title("Countdown Timer")
            root.geometry("300x120")
            label = tk.Label(root, font=("Courier", 28), fg="lime", bg="black")
            label.pack(expand=True)
            root.attributes("-topmost", True)
            update()
            root.mainloop()
            return "yes"
        except Exception as e:
            print(f"Failed to start timer: {e}")
            return f"error occured {e}"

    def get_date(self):
        today = date.today().strftime("%Y-%m-%d")
        return today

    def check_time(self):
        current_time = datetime.now().strftime("%H:%M")
        return current_time

import json
import os

class MemoryManager:
    def __init__(self, max_window=20, window_size=2):
        self.full_history = []
        self.conversation_window = []
        self.max_window = max_window
        self.window_size = window_size

        # Paths to store JSON files
        self.full_history_path = "memory/full_history.json"
        self.conversation_window_path = "memory/conversation_window.json"

        # Load existing memory if present
        self.load_memory()

    def add_message(self, role, content):
        """
        Add a new message to the history and conversation window.
        """
        message = {"role": role, "content": content}
        self.full_history.append(message)
        self.conversation_window.append(message)

        if len(self.conversation_window) > self.max_window:
            self._summarize_oldest()

    def _summarize_oldest(self):
        self.conversation_window.pop(0)
    
    def get_prompt(self, system_prompt=None, separator="\n", window_size=2):
        prompt_parts = []

        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")

        # Only keep the last N messages
        recent = self.conversation_window[-window_size*2:]  # N user + N assistant

        for msg in recent:
            role_label = "Boss" if msg["role"] == "user" else "H.A.W.K."
            prompt_parts.append(f"{role_label}: {msg['content']}")

        return separator.join(prompt_parts)



    def get_full_history(self):
        return self.full_history

    def clear_memory(self):
        self.conversation_window = []
        print("\nMemory cleared.")

    def save_memory(self):
        os.makedirs("memory", exist_ok=True)
        with open(self.full_history_path, "w", encoding="utf-8") as f:
            json.dump(self.full_history, f, ensure_ascii=False, indent=2)
        with open(self.conversation_window_path, "w", encoding="utf-8") as f:
            json.dump(self.conversation_window, f, ensure_ascii=False, indent=2)
        print("\nMemory saved.")

    def load_memory(self):
        # Load full history
        if os.path.exists(self.full_history_path):
            with open(self.full_history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.full_history = data
                else:
                    print("Invalid data in full_history.json, starting fresh.")
                    self.full_history = []
        # Load conversation window
        if os.path.exists(self.conversation_window_path):
            with open(self.conversation_window_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.conversation_window = data
                else:
                    print("Invalid data in conversation_window.json, starting fresh.")
                    self.conversation_window = []

class PromptFileManager:
    def __init__(self, prompt_file="memory/prompt_history.txt", system_instructions=None):
        self.prompt_file = prompt_file
        self.system_instructions = system_instructions
        # Create file with system instructions if it doesn't exist
        if not os.path.exists(self.prompt_file):
            with open(self.prompt_file, "w", encoding="utf-8") as f:
                f.write("SYSTEM:\n")
                f.write(self.system_instructions.strip() + "\n\n")
                f.write("CONVERSATION:\n")

    def append_interaction(self, user_input, assistant_response):
        with open(self.prompt_file, "a", encoding="utf-8") as f:
            f.write(f"Boss: {user_input.strip()}\n")
            f.write(f"H.A.W.K.: {assistant_response.strip()}\n")

    def get_full_prompt(self):
        with open(self.prompt_file, "r", encoding="utf-8") as f:
            return f.read()

    def clear_conversation(self):
        with open(self.prompt_file, "w", encoding="utf-8") as f:
            f.write("SYSTEM:\n")
            f.write(self.system_instructions.strip() + "\n\n")
            f.write("CONVERSATION:\n")

class CalendarManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("H.A.W.K. Calendar")
        self.root.geometry("600x500")
        self.cal = Calendar(
            self.root,
            font=("Helvetica", 14),
            selectmode='day',
            year=date.today().year,
            width=400,
            height=300
        )
        self.cal.pack(pady=20)

        # Add buttons
        tk.Button(self.root, text="Show Events", command=self.show_events).pack(pady=5)
        tk.Button(self.root, text="Remove Events", command=self.remove_events).pack(pady=5)
        tk.Button(self.root, text="Add Event", command=self.add_event_dialog).pack(pady=5)

        # Sample event
        today = date.today()
        self.cal.calevent_create(today, "Today", 'today_highlight')

    def show_events(self):
        selected_date = datetime.strptime(self.cal.get_date(), "%m/%d/%y").date() 
        events = self.cal.get_calevents(date=selected_date)
        if not events:
            print("No events found.")
        else:
            for eid in events:
                print(self.cal.calevent_cget(eid, 'text'))

    def remove_events(self):
        selected_date = datetime.strptime(self.cal.get_date(), "%m/%d/%y").date()
        events = self.cal.get_calevents(date=selected_date)
        for eid in events:
            if 'today_highlight' not in self.cal.calevent_cget(eid, 'tags'):
                print(f"Removing event: {self.cal.calevent_cget(eid, 'text')}")
                self.cal.calevent_remove(eid)

    def add_event(self, event_name, date_str):
        self.cal.calevent_create(date_str, event_name, "user_event")

    def add_event_dialog(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text="Event name:").pack()
        entry = tk.Entry(top)
        entry.pack()
        def submit():
            self.add_event(entry.get())
            top.destroy()
        tk.Button(top, text="Add", command=submit).pack()

    def auto_show_events(self, date_str):
        events = self.cal.get_calevents(date=date_str)
        if not events:
            print("No events found.")
        else:
            for eid in events:
                print(self.cal.calevent_cget(eid, 'text'))

    def run(self):
        self.root.mainloop()

class AppLauncher:
    def __init__(self):
        # You can extend this dictionary to add more apps and their paths
        self.app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "spotify": r"C:\Users\YourUser\AppData\Roaming\Spotify\Spotify.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            # add more apps here
        }

    def open_app(self, app_name):
        app_name = app_name.lower()
        if app_name in self.app_paths:
            path = self.app_paths[app_name]
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.Popen([path])
                print(f"Opened {app_name}.")
            except Exception as e:
                print(f"Failed to open {app_name}: {e}")
        else:
            print(f"⚠️ App '{app_name}' not found in known paths.")

    def search_and_open(self, app_name):
        """
        Dynamically searches Program Files for the app executable.
        This is slower but helps when you don't have the path mapped.
        """
        search_dirs = [
            r"C:\\Program Files",
            r"C:\\Program Files (x86)",
            r"C:\\Users\\chenj\\AppData\\Local",
            r"C:\\Users\\chenj\\AppData\\Roaming"
        ]

        app_exe = app_name.lower() + ".exe"
        for dir_path in search_dirs:
            dir_path = os.path.expandvars(dir_path)
            for root, dirs, files in os.walk(dir_path):
                if app_exe in files:
                    exe_path = os.path.join(root, app_exe)
                    try:
                        os.startfile(exe_path)
                        print(f"Found and opened {app_name}: {exe_path}")
                        return
                    except Exception as e:
                        print(f"Failed to open {app_name}: {e}")
                        return
        print(f"Could not find '{app_exe}' on disk.")

    
    def find_exe_in_folder(self, app_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "installed_apps.json")

        with open(csv_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for app in data:
            if app.get("name", "").lower() == app_name.lower():
                app_path = app.get("install_location")
                break
        else:
            app_path = None
        if not app_path or not os.path.exists(app_path):
            print("Path does not exist!")
            print(f"App '{app_name}' not found in installed apps.")
            return None
        exe_files = glob.glob(os.path.join(app_path, "*.exe"))
        if not exe_files:
            exe_files = glob.glob(os.path.join(app_path, "**", "*.exe"), recursive=True)

        if not exe_files:
            print("No .exe files found.")
            return None
        if app_name:
            for exe in exe_files:
                if app_name.lower() in os.path.basename(exe).lower():
                    return exe
        return exe_files[0]

class TodoListManager:
    def __init__(self):
        self.db_path = "memory/Reminder.db"

    # Function to add a task
    def add_todo(self, task_text, location):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO todos (todo, location) VALUES (?, ?)", (task_text, location))
            conn.commit()
            conn.close()
            return "added"
        except Exception as e:
            print(f"[ERROR] Exception occurred while saving: {e}")
            return f"error occurred {e}"


    # Function to list tasks
    def list_todos(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT todo, latitude, longitude FROM todos")
            conn.commit()
            todos = cursor.fetchall()
            conn.close()
            if not todos:
                print("No tasks found.")
                return "no tasks found"
            return [todo[0] for todo in todos]
        except Exception as e:
            print(f"[ERROR] Exception occurred while listing: {e}")
            return f"error occurred {e}"


    # Function to remove a task by index
    def remove_todo(self, task):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM todos WHERE todo = ?", (task,))
            conn.commit()
            conn.close()
            if cursor.rowcount == 0:
                print(f"Task '{task}' not found in the todo list.")
                return "remove failed"
            return "removed"
        except Exception as e:
            print(f"[ERROR] Exception occurred while verifying: {e}")
            return f"error occurred {e}"


    def clear_todos(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM todos")
            conn.commit()
            conn.close()
            return "cleared"
        except Exception as e:
            print(f"[ERROR] Exception occurred while clearing tasks: {e}")
            return f"error occurred {e}"

    def check_todo(self, task):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM todos WHERE title = ?", (task,))
            todos = cursor.fetchall()
            conn.close()
            for todo in todos:
                if todo.lower() == task.lower():
                    print(f"✅ Task '{task}' is in the todo list.")
                    return "yes"
            print(f"Task '{task}' is not in the todo list.")
            return "task not found"
        except Exception as e:
            print(f"[ERROR] Exception occurred while checking task: {e}")
            return f"error occurred {e}"

class LocationManager:
    def __init__(self):
        self.db_path = "memory/Reminders.db"

    def add_location(self, location_name, latitude, longitude):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO locations (location_name, latitude, longitude) VALUES (?, ?, ?)", (location_name, latitude, longitude))
            conn.commit()
            conn.close()
            print(f"Location '{location_name}' added.")
            return "added"
        except Exception as e:
            print(f"[ERROR] Exception occurred while saving location: {e}")
            return f"error occurred {e}"

    def remove_location(self, location_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM locations WHERE location_name = ?", (location_name,))
            conn.commit()
            conn.close()
            if cursor.rowcount == 0:
                print(f"Location '{location_name}' not found.")
                return "remove failed"
            print(f"Location '{location_name}' removed.")
            return "removed"
        except Exception as e:
            print(f"[ERROR] Exception occurred while removing location: {e}")
            return f"error occured {e}"

class NewLocationManager:
    def __init__(self):
        self.knowledge_path = "knowledge.py"

    def add_location(self, location_name, latitude, longitude):
        with open(self.knowledge_path, "a") as f:
            f.write(f"Location: {location_name}, Latitude: {latitude}, Longitude: {longitude}\n")
        print(f"Location '{location_name}' added.")
        return "added"

    def remove_location(self, location_name):
        with open(self.knowledge_path, "r") as f:
            lines = f.readlines()
        with open(self.knowledge_path, "w") as f:
            for line in lines:
                if line.strip() != f"Location: {location_name}":
                    f.write(line)
        print(f"Location '{location_name}' removed.")
        return "removed"

class RemindersManager:
    def __init__(self):
        self.db_path = "memory/Reminders.db"

    def mobile_notify(self, token: str, title: str, body: str):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
        )
        response = messaging.send(message)
        print("Successfully sent message:", response)


    def fix_when_to_remind(self, arg: str) -> str:
        arg = arg.strip().lower()
        today = datetime.now()

        # Handle special phrases manually
        if "this weekend" in arg:
            # Get next Friday at 7:00 PM
            friday_offset = (4 - today.weekday()) % 7  # 4 = Friday
            dt = today + timedelta(days=friday_offset)
            return dt.replace(hour=19, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

        elif "next weekend" in arg:
            # Friday next week
            friday_offset = ((4 - today.weekday()) % 7) + 7
            dt = today + timedelta(days=friday_offset)
            return dt.replace(hour=19, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

        # Use dateparser for other phrases
        dt = dateparser.parse(arg, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': today,
            'PARSERS': ['relative-time', 'absolute-time', 'timestamp']
        })

        if dt:
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        # If parsing fails
        return arg

    def add_reminder(self, task, to_remind):
        try:
            to_remind = self.fix_when_to_remind(to_remind)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO reminders (task, to_remind)
            VALUES (?, ?)
            """, (task, to_remind))

            conn.commit()
            conn.close()

            print(f"Reminder '{task}' added for {to_remind}.")
            return "added"

        except sqlite3.Error as e:
            print(f"Error adding reminder: {e}")
            return f"error occured {e}"

    def delete_reminder(self, task):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            DELETE FROM reminders WHERE task = ?
            """, (task,))

            conn.commit()
            conn.close()
            
            print(f"Reminder with task '{task}' deleted.")
            return "deleted"
        except sqlite3.Error as e:
            print(f"Error deleting reminder: {e}")
            return f"error occured {e}"

    def list_reminders(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders")
            reminders = cursor.fetchall()
            conn.close()

            if reminders:
                result = []
                for reminder in reminders:
                    status = "Done" if reminder[3] else "Not Done"
                    result.append(f"ID: {reminder[0]}, Task: {reminder[1]}, To Remind: {reminder[2]}, Status: {status}")
                return result
            else:
                return ["No reminders found."]
        except sqlite3.Error as e:
            print(f"Error listing reminders: {e}")
            return ["error"]


    def mark_reminder_done(self, task):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
            UPDATE reminders SET done = 1 WHERE task = ?
            """, (task,))

            conn.commit()
            conn.close()
            
            print(f"Reminder '{task}' marked as done.")
            return "yes"
        except sqlite3.Error as e:
            print(f"Error marking reminder as done: {e}")
            return "error"

    def get_due_reminders(self, fcm_token):
        if not fcm_token:
            print("⚠ No FCM token found. Skipping notification.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        past_time = now - timedelta(minutes=30)

        now_str = now.strftime("%Y-%m-%d %H:%M")
        past_str = past_time.strftime("%Y-%m-%d %H:%M")

        cursor.execute("""
            SELECT task FROM reminders
            WHERE to_remind > ? AND to_remind <= ?
        """, (past_str, now_str))

        results = [row[0] for row in cursor.fetchall()]
        conn.close()

        if results:
            noti = notifier.reminder_to_boss("\n".join(results))
            self.mobile_notify(fcm_token, "Due Reminders", noti)
            for result in results:
                self.delete_reminder(result)

    def trigger(self):
        try:
            with open(os.environ["FCM_TOKEN_PATH"]) as f:
                fcm_token = f.read().strip()
        except FileNotFoundError:
            print("⚠ fcm_token.txt not found.")
            return

        while True:
            self.get_due_reminders(fcm_token)
            time.sleep(900)  # every 15 mins


class NotificationManager():
    def __init__(self):
        self.title = "Notification"
        self.message = "Reminder from H.A.W.K."

    def notify(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="H.A.W.K.",
                timeout=10
            )
            print(f"Notification sent: {title} - {message}")
            return "notified"
        except ImportError:
            print("Plyer module not found. Please install it to use notifications.")
            return "error occured"

    

class Alarm():
    def __init__(self):
        self.alarm_time = None

    def set_alarm(self, time_str):
        try:
            self.alarm_time = datetime.strptime(time_str, "%H:%M")
            print(f"Alarm set for {self.alarm_time.strftime('%H:%M')}.")
            return "alarm set"
        except ValueError:
            print("Invalid time format. Use HH:MM.")
            return "error occured"

    def check_alarm(self):
        if self.alarm_time:
            now = datetime.now()
            if now.hour == self.alarm_time.hour and now.minute == self.alarm_time.minute:
                print("Alarm ringing!")
                return "ringing"
        return "not ringing"
    
# class UserManager:
#     def __init__(self, db_path="memory/Hawk_brain.db"):
#         self.db_path = db_path

#     def add_user(self, username):
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
#             conn.commit()
#             conn.close()
#         except sqlite3.Error as e:
#             print(f"Error adding user: {e}")
#     def check_username_exists(self, username):
#         try:
#             conn = sqlite3.connect(self.db_path)
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
#             user = cursor.fetchone()
#             conn.close()
#             return user is not None
#         except sqlite3.Error as e:
#             print(f"Error checking username: {e}")
#             return False
    
class InfoManager():
    def __init__(self):
        self.wiki_wiki = wikipediaapi.Wikipedia(user_agent='Hawk (merlin@example.com)', language='en')
        self.articles = []
        self.api_key = "058f233cb78b4e31b2f8fb7952c4b299"

    def search_wikipedia(self, query):
        page = self.wiki_wiki.page(query)
        if page.exists():
            return page.text
        else:
            return "No results found."

    def search_news(self, query):
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={self.api_key}"
        response = requests.get(url)
        data = response.json()

        if data.get("totalResults", 0) > 0:
            articles = []
            for i, article in enumerate(data["articles"], 1):
                if i > 5:
                    break
                articles.append({
                    "id": i,
                    "title": article.get("title"),
                    "source": article["source"].get("name"),
                    "description": article.get("content")
                })

            # Return JSON-formatted string
            return json.dumps({"articles": articles}, indent=4)

        else:
            return json.dumps({"articles": [], "message": "No articles found."}, indent=4)

class DeviceManager:
    def __init__(self):
        self.db_path = "memory/Reminders.db"

    def add_device(self, device_name, device_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO devices (name, id) VALUES (?, ?)", (device_name, device_id))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error adding device: {e}")

    def remove_device(self, device_name):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM devices WHERE name = ?", (device_name,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error removing device: {e}")

if __name__ == "__main__":
    loc = AppLauncher()
    loc.search_and_open("LM Studio")