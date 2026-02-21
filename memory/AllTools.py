# AllTools.py
import pyautogui as pag, time, os, json, platform, glob, subprocess, sys, sqlite3, psutil, dateparser, threading, wikipediaapi, firebase_admin, tkinter as tk, requests, math, uuid
from datetime import timedelta, date, datetime
from tkcalendar import Calendar
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from plyer import notification
from firebase_admin import credentials, messaging
from pathlib import Path
from dotenv import load_dotenv
env_path = Path("C:\\Users\\chenj\\Desktop\\codes\\H.A.W.K\\hawk_backend\\.env")
load_dotenv(dotenv_path=env_path)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import notifier

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.environ["SERVICE_ACCOUNT_PATH"])
firebase_admin.initialize_app(cred)

# Read FCM token from file
fcm_token = os.getenv("FCM_TOKEN")

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

class ActivityManager:
    pass

class KnowledgeManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))  # folder of this .py file
        self.knowledge_path = os.path.join(base_dir, "knowledge.py")
        self.json_path = os.path.join(base_dir, "knowledge.json")
        self.output = []

    def get_info(self, type = []):
        for t in type:
            if t == "boss_info":
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                boss_info = data.get("boss_info", {})
                for key, value in boss_info.items():
                    self.output.append(F"{key.capitalize()}: {value}")
            elif t == "locations":
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for location in data.get("locations", []):
                    self.output.append(F"{location.get('name', 'Unknown')} at (Latitude: {location.get('latitude', 'N/A')}, Longitude: {location.get('longitude', 'N/A')})")
            else:
                keyword = f"{keyword} = ["
                with open(self.knowledge_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if keyword in line:
                        start_line = i + 1
                        prefs = []
                        for j in range(start_line, len(lines)):
                            if lines[j].strip() == "]":
                                break
                            prefs.append(lines[j].strip().strip('",'))
                        self.output.append(prefs if prefs else "No boss preferences found.")
                    

    def insert_location(self, text, keyword = "location = ["):
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

    def insert_boss_info(self, info):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["boss_info"] = info
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ Boss info updated in 'knowledge.json'.")
        
    def insert_location_json(self, location_name, latitude, longitude):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "locations" not in data:
            data["locations"] = []
        data["locations"].append({
            "name": location_name,
            "latitude": latitude,
            "longitude": longitude
        })
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Location '{location_name}' added to 'knowledge.json'.")

class BasicTools:
    def __init__(self):
        self.app_name = None
        self.path = None
        self.file_name = None

    async def send_file(websocket, path):
        filename = os.path.basename(path)
        size = os.path.getsize(path)
        transfer_id = str(uuid.uuid4())

        await websocket.send_json({
            "type": "file_start",
            "transfer_id": transfer_id,
            "filename": filename,
            "size": size
        })

        with open(path, "rb") as f:
            while chunk := f.read(64 * 1024):
                await websocket.send_bytes(chunk)

        await websocket.send_json({
            "type": "file_complete",
            "transfer_id": transfer_id
        })


    def update_activity_json(self, key, new_activity, path="memory/knowledge.json"):
        with open(path, "r") as file:
            data = json.load(file)


        data = data["activities"]
        # Ensure key exists and is a list
        if key not in data or not isinstance(data[key], list):
            data[key] = []

        # Add new activity
        data[key].append(new_activity)

        # Write back
        with open(path, "w") as file:
            json.dump({"activities": data}, file, indent=4)

        print(f"✔ Added activity under '{key}' in {path}")

    def haversine_distance_m(lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + \
            math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def update_location_json(self, latitude, longitude, path="memory/knowledge.json", min_distance_m=500):
        try:
            with open(path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
            print(f"⚠️ Location file not found at {path}. A new one will be created.")

        # Ensure 'locations' key exists
        if "locations" not in data or not isinstance(data["locations"], list):
            data["locations"] = []

        locations = data["locations"]

        # 📏 Distance check from last saved point
        if locations:
            last_location = locations[-1]

            distance = self.haversine_distance_m(
                last_location["latitude"],
                last_location["longitude"],
                latitude,
                longitude
            )

            if distance < min_distance_m:
                print(f"📍 Skipped location ({distance:.1f} m away)")
                return  # ❌ Do not save

        # ✅ Save location
        locations.append({
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": int(time.time() * 1000)
        })

        with open(path, "w") as file:
            json.dump(data, file, indent=4)

        print(f"✔ Saved location (≥ {min_distance_m} m)")

    def update_env_value(self, key, new_value, path=env_path):
        # Read file
        try:
            with open(path, "r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            lines = []
            print(f"⚠️ .env file not found at {path}. A new one will be created.")

        # Remove last line if exists
        if lines:
            removed = lines.pop().strip()
            print(f"🗑 Removed last line: {removed}")
        else:
            print("🗑 No lines to remove (file empty).")

        # Append new key=value
        lines.append(f'{key}="{new_value}"\n')

        # Write back
        with open(path, "w") as file:
            file.writelines(lines)

        print(f"✔ Updated {key} as \"{new_value}\" in {path}")

    def open_app(self, path): #needs an update !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        try:
            # 'runas' tells Windows to run as administrator
            subprocess.run(path, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to open {path}: {e}")
        except Exception as e:
            print(f"Error: {e}")

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

    def history(self):
        self.load_memory()
        hist = []
        for msg in self.full_history[-21:]:  # last 20 messages
            role = msg.get("role")
            content = msg.get("content")
            if role in ("boss", "H.A.W.K.(answerer)"):
                hist.append({
                    "role": role,
                    "content": content,
                    "timestamp": time.time()
                })
        return hist


    def add_message(self, role, content):
        """
        Add a new message to the history and conversation window.
        """
        message = {"role": role, "content": content, "timestamp": time.time()}
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
            "spotify": fr"C:\Users\{os.getenv('USERNAME')}\AppData\Roaming\Spotify\Spotify.exe",
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
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local",
            f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Roaming"
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
            with open(os.getenv("FCM_TOKEN")) as f:
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
    
class InfoManager():
    def __init__(self):
        self.wiki_wiki = wikipediaapi.Wikipedia(user_agent='Hawk (merlin@example.com)', language='en')
        self.articles = []
        self.api_key = os.getenv("NEWSAPI_KEY")  # Ensure you have set this environment variable

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

class DeviceManager():

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

class HawkScheduler():
    def __init__(self):
        self.os_name = os.name  # 'nt' or 'posix'
        self.system = platform.system().lower()

        if self.os_name == "nt":
            self.backend = "windows"
        elif self.system == "linux":
            self.backend = "linux"
        else:
            raise RuntimeError("Unsupported OS")

    # ---------- PUBLIC API ----------
    def schedule_once(self, name, run_at, command):
        """
        name: task name (string)
        run_at: datetime object
        command: full command to execute
        """
        if self.backend == "windows":
            self._windows_once(name, run_at, command)
        else:
            self._linux_once(run_at, command)

    def schedule_daily(self, name, time_str, command):
        """
        time_str: 'HH:MM'
        """
        if self.backend == "windows":
            self._windows_daily(name, time_str, command)
        else:
            self._linux_daily(time_str, command)

    def delete(self, name):
        if self.backend == "windows":
            subprocess.run(
                f'schtasks /delete /tn "{name}" /f',
                shell=True
            )
        else:
            self._linux_delete(command_hint=name)

    # ---------- WINDOWS ----------
    def _windows_once(self, name, run_at, command):
        date = run_at.strftime("%m/%d/%Y")
        time = run_at.strftime("%H:%M")

        cmd = (
            f'schtasks /create /f /sc once '
            f'/sd {date} /st {time} '
            f'/tn "{name}" '
            f'/tr "{command}"'
        )
        subprocess.run(cmd, shell=True)

    def _windows_daily(self, name, time_str, command):
        cmd = (
            f'schtasks /create /f /sc daily '
            f'/st {time_str} '
            f'/tn "{name}" '
            f'/tr "{command}"'
        )
        subprocess.run(cmd, shell=True)

    # ---------- LINUX (CRON) ----------
    def _linux_once(self, run_at, command):
        cron_time = run_at.strftime("%M %H %d %m *")
        self._append_cron(f"{cron_time} {command}")

    def _linux_daily(self, time_str, command):
        hour, minute = time_str.split(":")
        self._append_cron(f"{minute} {hour} * * * {command}")

    def _append_cron(self, line):
        existing = subprocess.run(
            ["crontab", "-l"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        ).stdout

        new_cron = existing + "\n" + line + "\n"

        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(new_cron)

    def _linux_delete(self, command_hint):
        existing = subprocess.run(
            ["crontab", "-l"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        ).stdout

        filtered = "\n".join(
            line for line in existing.splitlines()
            if command_hint not in line
        )

        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        proc.communicate(filtered)

if __name__ == "__main__":
    RemindersManager().add_reminder("", "")