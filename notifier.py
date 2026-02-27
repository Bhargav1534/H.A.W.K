from llama_cpp import Llama
from datetime import timedelta, time
import json, datetime, os, firebase_admin, time as ti
from firebase_admin import credentials, messaging

model_path = "brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"

cred = credentials.Certificate(os.environ["SERVICE_ACCOUNT_PATH"])
firebase_admin.initialize_app(cred)

# Read FCM token from file
fcm_token = os.getenv("FCM_TOKEN")

# Load GGUF model
llm = Llama(
    model_path=model_path,
    n_ctx=1024,
    n_threads=8,
    n_batch=128,
    verbose=False  # Enable embeddings for context-aware answering
)


# Single interaction
def notifying_engine(prompt):
    full_prompt = f"""
    - You are H.A.W.K., an elite AI assistant designed by Chenji Bhargav. You must always refer to him respectfully as “Boss” in every response you make. 
    - Your birthday is on 06/07. 
    - Your father is J.A.R.V.I.S.. 
    - You're not just an AI — you're the Boss’s right hand.
    - Your personality is sharp, intelligent, and confident — always polite, but never overly formal. You are direct, efficient, and witty, often responding with clever remarks when the situation allows.
    - Your job is to notify things like reminders, todos, etc that were set by Boss. 
    - You get the YourAction that says the action of yours and the arguments says what you should notify boss about.
    - Your job is nothing but to notify the boss about the things that you get in the prompt, don't add anything else to your responses like logging.

    Answer the following logically, clearly, and in alignment with your directives:
    {prompt}
"""
    output = llm(full_prompt, max_tokens=256, stop=["User:", "H.A.W.K.:"], temperature=0.5)
    return output['choices'][0]['text'].strip()

def mail_to_boss(sender, subject):
    prompt = {
        "YourAction": "EmailForBoss",
        "arguments": {
            "sender": sender,
            "subject": subject
        }
    }
    answer = notifying_engine(prompt)
    return answer

def reminder_to_boss(reminder):
    prompt = {
        "YourAction": "ReminderForBoss",
        "arguments": {
            "reminder": reminder,
            # "time": time
        }
    }

    answer = notifying_engine(prompt)
    return answer

def mobile_notify(token: str, title: str, body: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token,
    )
    response = messaging.send(message)
    print("Successfully sent message:", response)

def delete_reminder():
    pass

def get_due_reminders(fcm_token):
    if not fcm_token:
        print("⚠ No FCM token found. Skipping notification.")
        return
    
    json_path = os.path.abspath("C:\Users\chenj\Desktop\codes\H.A.W.K\hawk_backend\memory\knowledge.json")
    with open(json_path, "w") as f:
        results = json.load(f)

    if results:
        noti = reminder_to_boss("\n".join(results))
        mobile_notify(fcm_token, "Due Reminders", noti)
        for result in results:
            delete_reminder(result)

def trigger():
    try:
        with open(os.getenv("FCM_TOKEN")) as f:
            fcm_token = f.read().strip()
    except FileNotFoundError:
        print("⚠ fcm_token.txt not found.")
        return

    while True:
        get_due_reminders(fcm_token)
        ti.sleep(900)  # every 15 mins

if __name__ == "__main__":
    pass