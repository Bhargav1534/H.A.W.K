# from llama_cpp import Llama
# import time

# # model_paths = ["brain\\models\\HX-Mistral-1.5B_v0.3.Q2_K.gguf", "brain\\models\\Qwen3-4B-Thinking-2507-Q8_0.gguf", "brain\\models\\HX-Mistral-1.5B_v0.3.Q6_K.gguf", "brain\\models\\llama-3.2-1b-instruct-q8_0.gguf", "brain\\models\\deepseek-coder-1.3B-kexer-Q8_0.gguf", "brain\\models\\Yi-Coder-1.5B-Q8_0.gguf", "brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"]

# model_paths = ["brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"]

# i = "add a reminder for vaccuming the house at tomorrow 10:00 pm"
# with open("prompt.txt", "r", encoding="utf-8") as f:
#     prompt = f.read()
# prompt += f"{i}\nAssistant:"
# for mp in model_paths:
#     print("\n\n=== Using model:", mp, "===\n")
#     starttime = time.time()
#     llm = Llama(model_path=mp, n_ctx=32768, n_threads=8, n_batch=1024, verbose=False)
#     response = llm(prompt=prompt, max_tokens=512, stop=["Boss:", "Assistant:", "\n\n", "assistant:"], temperature=0.1, top_p=0.7, frequency_penalty=0.0, presence_penalty=0.0)
#     print("Assistant:", response['choices'][0]['text'])
#     endtime = time.time()
#     print("Time taken:", endtime - starttime)

import json,faiss, numpy as np 
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer("all-MiniLM-L6-v2")

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


with open("memory/knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Example use
text_data = boss_info_to_text(data)
print("Text data for boss info:", text_data)
embeddings = embedder.encode(text_data, convert_to_numpy=True)
embeddings = np.atleast_2d(embeddings)
dimension = embeddings.shape[1]
info_index = faiss.IndexFlatL2(dimension)
info_index.add(embeddings)

def retrieve_boss_info(data, k=3) -> list[str]:    
    enc = embedder.encode([data], convert_to_numpy=True)
    D, I = info_index.search(enc, k)
    return [text_data[i] for i in I[0] if i < len(text_data)]

info = retrieve_boss_info("What is my sbi account number?")
print("Retrieved info:", info)