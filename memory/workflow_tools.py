import pyautogui, time, os, json, platform, glob, subprocess, sys, sqlite3, psutil, dateparser, threading, wikipediaapi, firebase_admin, tkinter as tk, requests, math
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
cred = credentials.Certificate(os.environ["SERVICE_ACCOUNT_PATH"])
firebase_admin.initialize_app(cred)

# Read FCM token from file
fcm_token = os.getenv("FCM_TOKEN")

class HidInputTools:
    def __init__(self):
        pass

    def move_mouse(x: int, y: int, duration: float = 0.5):
        pyautogui.moveTo(x, y, duration=duration)

    def click_mouse(x: int, y: int, button: str):
        pyautogui.click(x, y, button=button)

    def scroll_mouse(amount: int):
        pyautogui.scroll(amount)

    def get_mouse_position():
        return pyautogui.position()

    def drag_mouse(x: int, y: int, duration: float = 0.5, button: str = 'left'):
        pyautogui.dragTo(x, y, duration=duration, button=button) 

    def type_text(text: str, interval: float = 0.1):
        pyautogui.write(text, interval=interval)

    def press_key(key: str):
        pyautogui.press(key)

    def hotkey(*keys):
        pyautogui.hotkey(*keys)

    def partial_screenshot(region: tuple = None):
        return pyautogui.screenshot(region=region)
    
    def screenshot(save_path: str):
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)

    def alert(message: str, title: str = 'Alert'):
        pyautogui.alert(text=message, title=title)

    def confirm(message: str, title: str = 'Confirm'):
        return pyautogui.confirm(text=message, title=title)
    
    def know_cwd(self):
        return os.getcwd()
    
class FileFolderTools:
    def __init__(self):
        pass

    def read_file(file_path: str):
        with open(file_path, 'r') as file:
            return file.read()

    def write_file(file_path: str, content: str):
        with open(file_path, 'w') as file:
            file.write(content)

    def create_folder(folder_path: str):
        os.makedirs(folder_path, exist_ok=True)

    def change_folder(folder_path: str):
        return os.chdir(folder_path)
    
    def check_exists(file_path: str):
        return os.path.exists(file_path)
    
    def check_folder_exists(folder_path: str):
        return os.path.isdir(folder_path)
        

class ChecksLoops:
    def __init__(self):
        pass
        
    def check_dir(dir_path: str):
        return True if os.getcwd() == dir_path else False
    
    def check_event(event_name: str):
        pass

    def actively_wait_for_event(event_name: str, timeout: int):
        pass

class BasicTools:
    def __init__(self):
        self.app_name = None
        self.path = None
        self.file_name = None

    def update_activity_json(self, key, new_activity, path="memory/knowledge.json"):
        try:
            with open(path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"phone_activity": [], "browser_activity": [], "pc_activity": []}
            print(f"⚠️ Activity file not found at {path}. A new one will be created.")

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
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        pyautogui.write(self.file_name, interval=0.05)
        pyautogui.press('enter')
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
        today = datetime.today().strftime("%Y-%m-%d")
        return today

    def check_time(self):
        current_time = datetime.now().strftime("%H:%M")
        return current_time
    
    def mobile_notify(self, title: str, body: str, token: str = fcm_token):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
        )
        response = messaging.send(message)
        print("Successfully sent message:", response)

if __name__ == "__main__":
    # os.chdir("memory")
    # if not os.path.exists("test_screenshots"):
    #     os.mkdir("test_screenshots")
    # HidInputTools.screenshot("test_screenshots/full_screenshot.png")
    pass