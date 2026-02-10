# from llama_cpp import Llama
# import time, memory.AllTools as tools

# model_path = "brain\\models\\Mistral-7B-Instruct-v0.3-Q8_0.gguf"
# # model_path = "brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"
# prompt = ""

# llm = Llama(model_path=model_path, n_ctx=2048, n_threads=8, verbose=True)

# # 1. For workflow testing
# with open("prompt/workflow_prompt.txt", "r", encoding="utf-8") as f:
#     prompt = f.read()


# # # 2. For event planning testing
# # tools = tools.MemoryManager()

# # convo = []
# # convo = tools.history()

# # with open("prompt/event_prompt.txt", "r", encoding="utf-8") as f:
# #     prompt = f.read()
# # prompt += f"\n{convo}" + f"\nDate: {time.strftime('%Y-%m-%d')}"


# start = time.time()
# inp = input("Enter your input: ")
# prompt = prompt + f"\nUser: {inp}\nAssistant:"
# print(prompt)
# output = llm(prompt=prompt, max_tokens=512, temperature=0.7)
# end = time.time()
# print("Response:\n", output["choices"][0]["text"])
# print(f"Time taken: {end - start:.2f} seconds")

# import requests

# h = requests.get("https://video.google.com/timedtext?type=list&v=bz67tNeE_s4").text
# print(h)

import requests
import xml.etree.ElementTree as ET

video_id = "bE4aTaU_aLo"
url = f"https://video.google.com/timedtext?lang=en&v={video_id}"

res = requests.get(url)

root = ET.fromstring(res.text)

print("Text elements found:", root.findall("text"))

captions = []
try:
    for text in root.findall("text"):
        captions.append(text.text)

    final_text = " ".join(captions)
except ET.ParseError:
    final_text = "No captions found or unable to parse captions."
print(final_text)
