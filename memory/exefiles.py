import os
import win32com.client
import json

def get_all_shortcuts():
    shell = win32com.client.Dispatch("WScript.Shell")
    locations = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expanduser(r"~\AppData\Local\Programs"),
        os.path.expanduser(r"~\AppData\Roaming"),
    ]

    apps = {}
    for loc in locations:
        if not os.path.exists(loc):
            continue
        for root, _, files in os.walk(loc):
            for f in files:
                if f.lower().endswith(".lnk"):
                    try:
                        lnk_path = os.path.normpath(os.path.join(root, f))
                        shortcut = shell.CreateShortcut(lnk_path)
                        target = shortcut.TargetPath

                        if target and target.lower().endswith(".exe"):
                            app_name = os.path.splitext(f)[0]
                            apps[app_name] = target
                    except Exception:
                        pass
    return apps

# Save output
os.makedirs("memory", exist_ok=True)

apps = get_all_shortcuts()
with open("memory/startmenu_executables.json", "w", encoding="utf-8") as f:
    json.dump(apps, f, indent=4, ensure_ascii=False)

for app, path in apps.items():
    print(app, path)
    with open("knowledge.py", "a", encoding="utf-8") as kf:
        kf.write(f'"app_name: {app}, its path: {path.replace("\\", "\\\\")}",\n')

print("✅ Shortcut scan complete.")
