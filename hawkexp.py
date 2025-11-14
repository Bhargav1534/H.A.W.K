# hawk.py
import re, json, faiss, time, ast, pyttsx3, memory.AllTools as tools, memory.knowledge as tk, classify as cl
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
from datetime import date

# To measure time between points
def time_measure(start) -> float:
        end_time = time.time()
        return end_time - start

# Text-to-Speech function
def speak(text, rate=160, voice_index=2) -> None:
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    voices = engine.getProperty('voices')
    if voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)
    time.sleep(0.2)  # small buffer
    engine.say(text)
    engine.runAndWait()

# model path initialization
model_path = "brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"
model_path2 = "brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"

# Getting instructions and format for the llm to follow
with open("prompt/instructions.txt", "r", encoding="utf-8") as f:
    instructions = f.read()
with open("prompt/format.txt", "r", encoding="utf-8") as f:
    format = f.read()

# === EMBEDDING & VECTOR STORE SETUP ===
with open("memory/knowledge.json", "r", encoding="utf-8") as f:
    boss_info = json.load(f)

# used to build the vector database for information retrieval
# 1. Load embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2")
classify_data = []

# 2. Encode tools
def boss_info_to_text(data):    
    boss = data.get("boss_info", {})
    sentences = []

    for key, value in boss.items():
        is_list = False
        # handle lists (like hobbies)
        if isinstance(value, list):
            value = ", ".join(value)
            if len(value.split(", ")) > 1:
                is_list = True
        # create clean readable sentence
        sentences.append(f"The {key} of the boss {'are' if is_list else 'is'} {value}.")
    return sentences

boss_info_text = boss_info_to_text(boss_info)
info_embeddings = embedder.encode(boss_info_text)
embeddings = embedder.encode(tk.tools)
embeddings2 = embedder.encode(tk.boss_prefs)
app_embed = embedder.encode(tk.app_info)
info_embed = embedder.encode(tk.info)

# 3. Setup FAISS index
dimension = embeddings.shape[1]
tools_index = faiss.IndexFlatL2(dimension)
tools_index.add(embeddings)

app_index = faiss.IndexFlatL2(dimension)
app_index.add(app_embed)

info_index = faiss.IndexFlatL2(dimension)
info_index.add(info_embed)

boss_info_index = faiss.IndexFlatL2(dimension)
boss_info_index.add(info_embeddings)

# 4. Encode boss prefs and add to the same index
def relevant_apps(user_input, k=5) -> list[str]:
    query_emb = embedder.encode([user_input])
    D, I = app_index.search(query_emb, k)
    return [tk.app_info[i] for i in I[0]]

def retrieve_tools(user_input, k=3) -> list[str]:
    query_emb = embedder.encode([user_input])
    D, I = tools_index.search(query_emb, k)
    return [tk.tools[i] for i in I[0]]

# def retrieve_prefs(user_input, k=3) -> list[str]:
#     query_emb = embedder.encode([user_input])
#     D, I = index.search(query_emb, k)
#     return [tk.boss_prefs[i] for i in I[0]]

# def retrieve_self_info(user_input, k=3) -> list[str]:
#     query_emb = embedder.encode([user_input])
#     D, I = index.search(query_emb, k)
#     return [tk.self_info[i] for i in I[0]]

def retrieve_info(query, k=3) -> list[str]:
    query_emb = embedder.encode([query])  # your existing search
    D, I = info_index.search(query_emb, k)
    # Make sure there are results
    if len(I) == 0 or len(I[0]) == 0:
        return []  # or return ["No relevant info found"]
    return [tk.info[i] for i in I[0] if i < len(tk.info)]  # extra safety

def retrieve_boss_info(data, k=3) -> list[str]:    
    enc = embedder.encode([data])
    D, I = boss_info_index.search(enc, k)
    return [boss_info_text[i] for i in I[0] if i < len(boss_info_text)]




# === TOOL INITIALIZATION ===
memtool = tools.MemoryManager()
basic = tools.BasicTools()
todo = tools.TodoListManager()
remtool = tools.RemindersManager()
loctool = tools.LocationManager()

# Smaller model for understanding engine
llm2 = Llama(
    model_path=model_path2,
    n_gpu_layers=8,
    n_ctx=32768,
    n_threads=8,
    n_batch=1024,
    verbose=False
)

# Larger model for answerer engine
llm = Llama(
    model_path=model_path,
    n_gpu_layers=8,
    n_ctx=32768,
    n_threads=8,
    n_batch=1024,
    verbose=False
)

def execute_action(tool, entities) -> str:
    if tool == "OpenApplication":
        print(f"Opening application at path: {entities.get('app_path', '')}")
        conclusion = basic.open_app(entities.get("app_path", ""))

    # elif tool == "AddTodoList":
    #     task = entities.get("task", "")
    #     loc = entities.get("location", {})
    #     conclusion = todo.add_todo(task, loc)

    # elif tool == "RemoveTodoList":
    #     task = entities.get("task", "")
    #     conclusion = todo.remove_todo(task)

    # elif tool == "ClearTodoList":
    #     conclusion = todo.clear_todos()

    # elif tool == "CheckTodoList":
    #     conclusion = todo.check_todo(entities.get("task", ""))

    # elif tool == "ListTodoList":
    #     conclusion = todo.list_todos()

    elif tool == "AddReminder":
        reminder = entities.get("reminder", "")
        when_to_remind = entities.get("when_to_remind", "")
        print(f"Adding reminder: {reminder} at {when_to_remind}")
        conclusion = remtool.add_reminder(reminder, when_to_remind)

    elif tool == "RemoveReminder":
        print(f"Removing reminder: {entities.get('reminder', '')}")
        conclusion = remtool.delete_reminder(entities.get("reminder", ""))

    elif tool == "ListReminders":
        conclusion = remtool.list_reminders()

    elif tool == "MarkReminderAsDone":
        print(f"Marking reminder as done: {entities.get('reminder', '')}")
        conclusion = remtool.mark_reminder_done(entities.get("reminder", ""))

    elif tool == "SetTimer":
        print(f"Setting timer for: {entities.get('duration', '')}")
        conclusion = basic.start_timer(entities.get("duration", ""))

    elif tool == "LockScreen":
        conclusion = basic.lock_system()

    elif tool == "ShutdownSystem":
        conclusion = basic.shutdown_system()

    elif tool == "RestartSystem":
        conclusion = basic.restart_system()

    elif tool == "SetVolume":
        volume = float(entities.get("volume", 50))  # Default to 50
        print(f"Setting volume to: {volume / 100}")
        conclusion = basic.set_volume(volume / 100)

    elif tool == "GetDate":
        conclusion = basic.get_date()

    elif tool == "CheckTime":
        conclusion = basic.check_time()

    elif tool == "AddLocation":
        name = entities.get("location_name", "")
        lat = entities.get("latitude", "")
        long = entities.get("longitude", "")
        print(f"Adding location: {name} at ({lat}, {long})")
        conclusion = loctool.add_location(name, lat, long)

    elif tool == "RemoveLocation":
        name = entities.get("location_name", "")
        print(f"Removing location: {name}")
        conclusion = loctool.remove_location(name)

    else:
        conclusion = "none"

    return conclusion

def append_with_limit(history, message, limit=2):
    history.append(message)
    if len(history) > limit:
        del history[0:len(history) - limit]


def parse_tool_entities(ans: str) -> tuple[str, dict]:
    # Clean markdown fences if any
    ans = re.sub(r'```(?:json)?', '', ans).strip()
    
    try:
        data = json.loads(ans)
    except json.JSONDecodeError:
        # Fallback for single quotes or non-JSON Python dicts
        try:
            data = ast.literal_eval(ans)
        except Exception:
            # Extract JSON substring as last resort
            match = re.search(r'\{[\s\S]*\}', ans)
            if match:
                try:
                    data = json.loads(match.group(0))
                except:
                    data = {}
            else:
                data = {}

    tool = data.get("Tool" or "tool", None)
    entities = data.get("Arguments" or "arguments", {})

    # If entities is a string containing JSON, load it
    if isinstance(entities, str):
        try:
            entities = json.loads(entities)
        except:
            try:
                entities = ast.literal_eval(entities)
            except:
                pass

    return tool, entities

    

chat_history_for_understander = []

def build_context_prompt_understander(history, current_input, tools_context, location, usable_apps) -> str:
    prompt = f"""{instructions}\nTime now is {time.strftime('%H:%M:%S')}\nDate today is {date.today().strftime("%Y-%m-%d")}\nTools to use: \n{tools_context}\n"Relevant apps:" \n{usable_apps if "OpenApplication" in tools_context else "None"}\nBoss's location: \n{location}\n"""
    for msg in history:
        role = "Boss" if msg["role"] == "boss" else "H.A.W.K.(understander)"
        prompt += f"{role}: {msg['content']}\n"
    prompt += f"Boss: {current_input}\nH.A.W.K.(understander):"
    return prompt


# === UNDERSTANDING ENGINE ===
def understanding_engine(prompt, tools_context, location, usable_apps) -> str:
    full_prompt = build_context_prompt_understander(chat_history_for_understander, prompt, tools_context, location, usable_apps)
    output = llm2(full_prompt, max_tokens=256, stop=["Boss:", "H.A.W.K.(understander):", "\n\n", "}"], temperature=0.5)
    answer = output['choices'][0]['text'].strip()+ "\n\t}\n}"
    print(f"Understanding Engine Raw Output: {answer}\n")
    match = re.search(r"\s*(\{(?:[^{}]*|\{[^{}]*\})*\})", answer)
    final = match.group(1) if match else "No valid response found."
    return final

# === CONTEXT-AWARE PROMPT BUILDER ===
def build_context_prompt_answerer(history, current_input, conclusion="none") -> str:
    prompt = f"""You are H.A.W.K., an elite AI assistant designed by Chenji Bhargav.
    - Always refer to him respectfully as 'Boss'.
    - Your birthday is on 06/07.
    - Your father is J.A.R.V.I.S..
    - Maintain a tone that is helpful, forward-thinking, and slightly playful when appropriate.
    - You're not just an AI — you're the Boss’s right hand.
    - Your personality is sharp, intelligent, and confident — always polite, but never overly formal.
    - You are direct, efficient, and witty, often responding with clever remarks when the situation allows.
    - The conclusion provided is for your understanding only, don't put this in your responses.

    Current time: {time.strftime('%H:%M:%S')}
    Current date: {date.today().strftime("%Y-%m-%d")}
"""

    for msg in history:
        role = msg["role"]
        content = msg["content"]
        if role == "boss":
            prompt += f"\nBoss: {content}"
        elif role == "H.A.W.K.(understander)":
            prompt += f"\nH.A.W.K.(understander): {content}"
        elif role == "H.A.W.K.(answerer)":
            prompt += f"\nH.A.W.K.(answerer): {content}"
        # if history has 'conclusion', include it
        if "conclusion" in msg and msg["conclusion"] != "none":
            prompt += f"\n[Conclusion: {msg['conclusion']}]"

    # Add current turn
    prompt += f"\nBoss: {current_input}"
    if conclusion != "none":
        prompt += f"\n[Conclusion: {conclusion}]"
    prompt += "\nH.A.W.K.(answerer):"

    return prompt

def classify_dataset_build(input_prompt, content) -> None:
        with open("memory/classify.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        classify_data = data if isinstance(data, list) else []
        classify_data.append({"input_prompt": input_prompt, "content": content})
        with open("memory/classify.json", "w", encoding="utf-8") as f:
            json.dump(classify_data, f, ensure_ascii=False, indent=4)


# === MAIN LOGIC ===
chat_history_for_answerer = []

def stream_hawk(input_prompt: str, location: str):
    conclusion = "none"
    tool, entities = None, {}
    input_prompt = input_prompt.strip()
    # classify_eval("boss", input_prompt)
    memtool.add_message("boss", input_prompt)
    classify_input = cl.classify_input(input_prompt)
    classify_dataset_build(input_prompt, classify_input)
    print(f"Classified Input: {classify_input}")
    relevant_info = retrieve_info(input_prompt, k=3)
    info_context = "\n".join(relevant_info)
    print(f"\nBoss: {input_prompt}\n")
    print(f"Boss's location: {location}")
    print(f"Relevant Info:\n{info_context}\n")
    if classify_input == "tool-use":
        append_with_limit(chat_history_for_understander, {"role": "boss", "content": input_prompt})
        relevant_tools = retrieve_tools(input_prompt, k=3)
        tools_context = "\n".join(relevant_tools)
        print(f"Relevant Tools:\n{tools_context}\n")
        usable_apps = relevant_apps(input_prompt, k=5)
        print(f"Usable Apps:\n{usable_apps}\n")
        st = time.time()
        ans = understanding_engine(input_prompt, tools_context, location, usable_apps)
        if __name__ == "__main__":
            et = time_measure(st)
            print(f"Understanding Engine Time Taken: {et:.2f} seconds")
        print(f"\nUnderstanding Engine Output: {ans}\n")
        append_with_limit(chat_history_for_understander, {"role": "H.A.W.K.(understander)", "content": ans})
        tool, entities = parse_tool_entities(ans)
        if tool == None:
            conclusion = ""
        conclusion = execute_action(tool, entities)
        print(f"\nExecution Conclusion: {conclusion}\n")
        append_with_limit(chat_history_for_answerer, {"role": "H.A.W.K.(understander)", "content": ans, "conclusion": conclusion})
        ans += f", Conclusion: {conclusion}"
        memtool.add_message("H.A.W.K.(understander)", ans)
    else:
        append_with_limit(chat_history_for_answerer, {"role": "boss", "content": input_prompt, "conclusion": conclusion})

    response_prompt = build_context_prompt_answerer(chat_history_for_answerer, input_prompt, conclusion)
    output = ""
    for chunk in llm(response_prompt, max_tokens=1024, stop=[ "Boss:", "H.A.W.K.(understander):", "H.A.W.K.(answerer):"], temperature=0.5, stream=True):
        content = chunk.get("choices", [{}])[0].get("text", "")
        if content.strip():
            output += content
            yield content

    append_with_limit(chat_history_for_answerer, {"role": "H.A.W.K.(answerer)", "content": output})

    # speak(output)
    memtool.add_message("H.A.W.K.(answerer)", output)
    memtool.save_memory()

if __name__ == "__main__":
    while True:
        try:
            input_prompt = input("Boss: ")
            start_time = time.time()
            location = {'longitude': 77.7116729, 'latitude': 12.9728962, 'timestamp': 1757061632081, 'accuracy': 5.205999851226807, 'altitude': 829.5, 'altitude_accuracy': 4.2094902992248535, 'floor': None, 'heading': 0.0, 'heading_accuracy': 0.0, 'speed': 0.0, 'speed_accuracy': 0.07052291184663773, 'is_mocked': False, 'gnss_satellite_count': 0.0, 'gnss_satellites_used_in_fix': 0.0}
            if input_prompt.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye Boss.")
                speak("Goodbye Boss.")
                break
            for token in stream_hawk(input_prompt, location):
                print(token, end="", flush=True)
            elapsed_time = time.time() - start_time
            print(f"\n⏱️ Elapsed Time: {elapsed_time:.2f} seconds")
        except KeyboardInterrupt:
            print("\n⛔ Interrupted. Ending session.")
            break