# import memory.AllTools as tools
# from pathlib import Path
# from dotenv import load_dotenv
# env_path = Path("C:\\Users\\chenj\\Desktop\\codes\\H.A.W.K\\hawk_backend\\.env")
# load_dotenv(dotenv_path=env_path)

# fcm_token = "fvQdchh3TcGEqA8mn_Kgbs"

# bas = tools.BasicTools()
# bas.update_env_value("FCM_TOKEN", fcm_token)
# import os
# import subprocess

# def open_app(path):
#         try:
#             subprocess.Popen(path)
#             print(f"{path} opened successfully!")
#         except Exception as e:
#             print(f"Failed to open {path}: {e}")
# if __name__ == "__main__":
#     app_to_open = "C:\\Program Files (x86)\\GPU-Z\\GPU-Z.exe"
#     open_app(app_to_open)

import subprocess
import sys

def open_app_as_admin(path):
    try:
        # 'runas' tells Windows to run as administrator
        subprocess.run(path, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to open {path}: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    app_path = "C:\\Program Files (x86)\\Steam\\steam.exe"
    open_app_as_admin(app_path)
