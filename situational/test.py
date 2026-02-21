# import firebase_admin, os
# from firebase_admin import credentials, messaging
# from pathlib import Path
# # from dotenv import load_dotenv
# # env_path = Path("C:\\Users\\chenj\\Desktop\\codes\\H.A.W.K\\hawk_backend\\.env")
# # load_dotenv(dotenv_path=env_path)

# fcm_token = os.getenv("FCM_TOKEN")
# # Initialize Firebase Admin with service account
# cred = credentials.Certificate("C:\\Users\\chenj\\Desktop\\codes\\secrets\\service-account.json")
# firebase_admin.initialize_app(cred)


# # Function to send push notification
# def send_push_notification(token: str, title: str, body: str):
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body,
#             # sound="sounds/feels_incomplete"  # No extension for Android
#         ),
#         token=token,
#         android=messaging.AndroidConfig(
#             priority="high",
#             notification=messaging.AndroidNotification(
#                 sound="feels_incomplete"  # Matches file name in res/raw
#             )
#         ),
#         apns=messaging.APNSConfig(
#             payload=messaging.APNSPayload(
#                 aps=messaging.Aps(
#                     sound="feels_incomplete.mp3"  # iOS can include extension
#                 )
#             )
#         )
#     )

#     response = messaging.send(message)
#     print(f"✅ Successfully sent message: {response}")

# send_push_notification(fcm_token, "H.A.W.K. Alert", "\nThis is a test notification from FastAPI!\n\n")

import time
from llama_cpp import Llama
import os

model_path = "C:\\Users\\chenj\\Desktop\\codes\\H.A.W.K\\hawk_backend\\brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"

model_path = os.path.abspath(model_path)

llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    n_threads=8,
    n_batch=1024,
    verbose=False,
    seed=42
)


def test_speed():
    prompt = """you are a helpful assistant that answers questions based on the following information:
    - you are a user asking your assistant to generate sentences based on the following information
    - You are the one is asking so only generate the sentences from your perspective. Do not generate sentences from the assistant's perspective.
    based on the following information:
    - Hey, send the project_report.pdf to my phone.
    - Transfer the latest APK build to my mobile device.
    - Can you share the resume.docx with my phone?
    - Push the notes.txt file to my phone over Wi-Fi.
    - Send that PDF we generated earlier to my phone now.
    - Upload the updated app APK to my phone and notify me when it’s done.
    - Share the file directly to my phone’s storage.
    - Transfer the document to my phone using the fastest available method.

    Now use these sentences as a reference and write a sentence
    """
    start_time = time.time()
    print(f"time of start: {start_time}")
    output = llm(prompt, max_tokens=256, stop=[], temperature=1)
    answer = output['choices'][0]['text'].strip()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Response: {answer}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    prompt += f"\nYou: {answer}\n make another sentence and don't repeat."

if __name__ == "__main__":
    x = 0
    start = time.time()
    while x < 100:
        print(f"Progress: {x+1}%")
        test_speed()
        x += 1
    end = time.time()
    total_time = end - start
    print(f"generate complete")
    print(f"Total time taken: {total_time:.2f} seconds")