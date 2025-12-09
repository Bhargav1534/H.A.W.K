# import memory.AllTools as tools
# from pathlib import Path
# from dotenv import load_dotenv
# env_path = Path("C:\\Users\\chenj\\Desktop\\codes\\H.A.W.K\\hawk_backend\\.env")
# load_dotenv(dotenv_path=env_path)

# fcm_token = "fvQdchh3TcGEqA8mn_Kgbs"

# bas = tools.BasicTools()
# bas.update_env_value("FCM_TOKEN", fcm_token)

import re
import os
from llama_cpp import Llama

MODEL_PATH = os.path.abspath(
    r"C:\Users\chenj\.lmstudio\models\lmstudio-community\Ministral-3-14B-Reasoning-2512-GGUF\Ministral-3-14B-Reasoning-2512-Q8_0.gguf"
)
MMPROJ_PATH = os.path.abspath(r"C:\Users\chenj\.lmstudio\models\lmstudio-community\Ministral-3-14B-Reasoning-2512-GGUF\mmproj-Ministral-3-14B-Reasoning-2512-F16.gguf"
)


# If you later want multimodal: add mmproj_path="path_to_mmproj.gguf"
llm = Llama(model_path=MODEL_PATH, mmproj_path=MMPROJ_PATH, n_ctx=8192)

prompt = """
Think step-by-step in <think> tags and give the final answer inside <answer> tags.

User: What is 27 × 41?
"""

def parse_think_answer(raw_text: str):
    """Return tuple (think_text, answer_text, raw_text)."""
    think_m = re.search(r"<think>(.*?)</think>", raw_text, re.S | re.I)
    answer_m = re.search(r"<answer>(.*?)</answer>", raw_text, re.S | re.I)

    think_text = think_m.group(1).strip() if think_m else ""
    answer_text = answer_m.group(1).strip() if answer_m else ""

    # If no <answer> tag, fall back to trying to find last line or whole output
    if not answer_text and raw_text:
        # try to take text after the last </think> if present
        split_after_think = re.split(r"</think>", raw_text, flags=re.I)
        if len(split_after_think) > 1:
            candidate = split_after_think[-1].strip()
            # remove tags if any remain
            candidate = re.sub(r"<.*?>", "", candidate).strip()
            answer_text = candidate

    return think_text, answer_text, raw_text

# Simple generation — no stop tokens (you'll get both <think> and <answer>)
resp = llm(prompt, max_tokens=256, temperature=0.0)  # temperature=0 for deterministic arithmetic
raw = resp["choices"][0]["text"]

think_text, answer_text, raw_text = parse_think_answer(raw)

print("=== RAW OUTPUT ===")
print(raw_text)
print("\n=== REASONING (<think>) ===")
print(think_text or "(no <think> block found)")
print("\n=== ANSWER (<answer>) ===")
print(answer_text or "(no <answer> block found; see raw output above)")
