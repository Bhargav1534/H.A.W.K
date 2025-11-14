import pyautogui as pag
import time
import os
import psutil

def is_app_running(process_name):
    """Check if any process contains the given name."""
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False



def open_whatsapp():
    # Launch WhatsApp Desktop (on Windows)
    if is_app_running("WhatsApp.exe"):
        os.system("taskkill /f /im WhatsApp.exe")  # Close if already running
    pag.hotkey('win', 's')
    time.sleep(1)
    pag.write("WhatsApp", interval=0.1)
    time.sleep(1)
    pag.press("enter")
    time.sleep(5)  # Wait for WhatsApp to open

def search_contact(contact_name):
    time.sleep(1)
    pag.write(contact_name, interval=0.1)
    time.sleep(2)
    pag.press("down")  # Navigate to the contact in the search results
    pag.press("enter")
    time.sleep(2)

def call_contact(call_type="voice"):
    # Position of the call buttons (depends on your screen!)
    if call_type == "voice":
        # Example: voice call button coords
        voice_call_btn = pag.locateOnScreen("C:\\Users\\chenj\\Desktop\\Projects\\W.A.T.E.R.(Witty Agent That Ends Rookies)\\memory\\Screenshot 2025-07-04 150836.png")
        if voice_call_btn:
            pag.click(voice_call_btn)
    elif call_type == "video":
        # Example: video call button coords
        pag.click(1700, 100)
    else:
        print("Unknown call type.")
    time.sleep(1)

if __name__ == "__main__":
    open_whatsapp()
    search_contact("thatha")
    call_contact("voice")  # Change to "video" for video calls
    print("Call initiated.")