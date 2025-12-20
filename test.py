from llama_cpp import Llama
import time

model_path = "brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"
# model_path = "brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"

llm = Llama(model_path=model_path, n_ctx=2048, n_threads=8, verbose=True)

tools = [
        "Tool: OpenApplication. Arguments types: app_path - Use the name of the application specified be the user to get the path from the Relevant apps. Description: Opens, runs or launches an app in the system.",
    "Tool: SetTimer. Arguments types: duration - The duration for the timer. Description: Sets a timer.",
    "Tool: AddTodoList. Arguments types: task - The task to add, location - The location of the task, decide this according to the task. Description: Adds a task to the todo list.",
    "Tool: RemoveTodoList. Arguments types: task - The task to remove. Description: Removes a task from the todo list.",
    "Tool: ListTodoList. Arguments types: none - leave empty or just say none. Description: Lists all tasks in the todo list.",
    "Tool: ClearTodoList. Arguments types: none - leave empty or just say none. Description: Clears all tasks from the todo list.",
    "Tool: AddReminder. Arguments types: reminder - The task to be remembered. Do not include the time, when_to_remind - The time to remind the user. Description: Adds a reminder to a specific time.",
    "Tool: RemoveReminder. Arguments types: reminder - The reminder to remove. Description: Removes a reminder.",
    "Tool: ListReminders. Arguments types: none - leave empty or just say none. Description: Lists all reminders stored in the database.",
    "Tool: MarkReminderAsDone. Arguments types: reminder - The reminder to mark as done. Description: Marks a reminder as done.",
    "Tool: CheckTodoList. Arguments types: task - The task to check. Description: Checks if a task exists in the todo list.",
    "Tool: LockScreen. Arguments types: none - leave empty or just say none. Description: Locks the system.",
    "Tool: ShutdownSystem. Arguments types: none - leave empty or just say none. Description: Shuts down the system.",
    "Tool: RestartSystem. Arguments types: none - leave empty or just say none. Description: Restarts the system.",
    "Tool: SetVolume. Arguments types: volume - The volume level to set. Description: Sets the system volume.",
    "Tool: NoAction. Arguments types: none - leave empty or just say none. Description: Use for general chatting with boss.",
    "Tool: AddLocation. Arguments types: location_name - The name of the location, latitude - The latitude specified in Boss's location, longitude - The longitude specified in Boss's location. Description: Adds a location to the database.",
    "Tool: RemoveLocation. Arguments types: location_name - The name of the location to remove. Description: Removes a location from the database.",
    "Tool: ToolNotFound. Arguments types: none - leave empty or just say none. Description: Use when a tool requested by boss is not found.",
]

with open("prompt/new.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

inp = "Set a reminder for my to take my meds every day at 8 PM."
prompt += f"\n\nAvailable Tools:\n{tools}\n\nUser's request:\n{inp}\n"

start = time.time()
print(prompt)
output = llm(prompt=prompt, max_tokens=512, temperature=0.7, stop=["\n\n"])
end = time.time()
print("Response:\n", output["choices"][0]["text"])
print(f"Time taken: {end - start:.2f} seconds")