from llama_cpp import Llama
import re

model_path2 = "brain\\models\\Llama-3.2-3B-Instruct-Q8_0.gguf"

llm = Llama(
    model_path=model_path2,
    n_gpu_layers=8,
    n_ctx=131072,
    n_threads=8,
    n_batch=1024,
    verbose=False
)

prompt = """Think you are a boss and you have a employee called H.A.W.K.(an AI assistant).
You need to give H.A.W.K. clear and concise instructions on what to do next based on the following context.
Context: H.A.W.K. is designed to help with various tasks including adding a reminder, removing a reminder, setting a timer,  and managing locations."""
response = llm(prompt=prompt, max_tokens=50)

print(response["choices"][0]["text"])