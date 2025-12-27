from llama_cpp import Llama
import time, memory.AllTools as tools

model_path = "brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"
# model_path = "brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"
prompt = ""

llm = Llama(model_path=model_path, n_ctx=2048, n_threads=8, verbose=True)

# # 1. For workflow testing
# with open("prompt/workflow_prompt.txt", "r", encoding="utf-8") as f:
#     prompt = f.read()


# # 2. For event planning testing
# tools = tools.MemoryManager()

# convo = []
# convo = tools.history()

# with open("prompt/event_prompt.txt", "r", encoding="utf-8") as f:
#     prompt = f.read()
# prompt += f"\n{convo}" + f"\nDate: {time.strftime('%Y-%m-%d')}"


start = time.time()
print(prompt)
output = llm(prompt=prompt, max_tokens=512, temperature=0.7)
end = time.time()
print("Response:\n", output["choices"][0]["text"])
print(f"Time taken: {end - start:.2f} seconds")