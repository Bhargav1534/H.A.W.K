import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase Admin with service account
cred = credentials.Certificate("C:\\Users\\chenj\\Desktop\\codes\\secrets\\service-account.json")
firebase_admin.initialize_app(cred)

# Function to send push notification
def send_push_notification(token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            # sound="sounds/feels_incomplete"  # No extension for Android
        ),
        token=token,
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                sound="feels_incomplete"  # Matches file name in res/raw
            )
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="feels_incomplete.mp3"  # iOS can include extension
                )
            )
        )
    )

    response = messaging.send(message)
    print(f"✅ Successfully sent message: {response}")

with open("C:\\Users\\chenj\\Desktop\\codes\\secrets\\fcm_token.txt", "r") as f:
    fcm_token = f.read().strip()


send_push_notification(fcm_token, "H.A.W.K. Alert", "\nThis is a test notification from FastAPI!\n\n")

# import os, subprocess, pyautogui

# def launch_app(app_path):
#     try:
#         os.startfile(app_path)
#         print("Launched with os.startfile")
#     except Exception as e:
#         try:
#             os.system(f"start \"{app_path}\"")
#             print("Launched with os.system")
#         except Exception as e:
#             try:
#                 subprocess.Popen([app_path])
#                 print("Launched with subprocess.Popen")
#             except Exception as e:
#                 try:
#                     pyautogui.hotkey('win', 's')
#                     pyautogui.write(app_path)
#                     pyautogui.press('enter')
#                     print("Launched with pyautogui")
#                 except Exception as e:
#                     print(f"Failed to launch application: {e}")

# launch_app("opera.exe")
# pyautogui.hotkey('win', 's')
# pyautogui.write("opera")
# pyautogui.press('enter')
# print("Launched with pyautogui")

# from llama_cpp import Llama, time

# model_path = "C:\\Users\\chenj\\.lmstudio\\models\\mradermacher\\mistral_28B_instruct_v0.2-GGUF\\mistral_28B_instruct_v0.2.Q6_K.gguf"

# llm = Llama(
#     model_path=model_path,
#     n_gpu_layers=8,
#     n_ctx=4096,
#     n_threads=8,
#     n_batch=1024,
#     verbose=False
# )


# def test_speed():
#     prompt = "what is chauffeur?"
#     start_time = time.time()
#     output = llm(prompt, max_tokens=256, stop=["Boss:", "H.A.W.K.(understander):", "\n\n", "}"], temperature=0.5)
#     answer = output['choices'][0]['text'].strip()+ "\n\t}\n}"
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Response: {answer}")
#     print(f"Time taken: {elapsed_time:.2f} seconds")

    