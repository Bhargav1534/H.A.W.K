from llama_cpp import Llama
import json, datetime

model_path = "brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"

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

if __name__ == "__main__":
    inp = "park bike"
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    result = reminder_to_boss(inp)
    print(f"🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    resu = "\n".join(result)
    print(resu)