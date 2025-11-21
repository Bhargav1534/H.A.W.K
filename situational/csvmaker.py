# import json
# import csv

# inp_file_path = "./memory/full_history.json"
# out_file_path = "./memory/full_history.csv"

# # Load JSON safely with UTF-8
# with open(inp_file_path, "r", encoding="utf-8") as f:
#     data = json.load(f)

# # Write CSV safely with UTF-8
# with open(out_file_path, "w", newline='', encoding="utf-8") as csvfile:
#     fieldnames = ["role", "content"]
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#     writer.writeheader()

#     for entry in data:
#         writer.writerow(entry)

# print("✅ Conversion complete! Saved as 'full_history.csv'")

import json
import csv


inp_file_path = "./memory/full_history.json"
out_file_path = "./memory/full_history.csv"

# Load your messages from a file (messages.json)
with open(inp_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
current_prompt = None

for msg in data:
    role = msg.get("role", "").lower()

    # Capture boss prompt
    if role == "boss":
        current_prompt = msg["content"]

    # Capture understander response
    elif "hawk.(understander" in role or "h.a.w.k.(understander" in role:
        if current_prompt is not None:
            rows.append({
                "prompt": current_prompt,
                "response": msg["content"]
            })
        current_prompt = None  # Reset for next pair

# Write to CSV
with open(out_file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["prompt", "response"])
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV generated: {out_file_path}")
