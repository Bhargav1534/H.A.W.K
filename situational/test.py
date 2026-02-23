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