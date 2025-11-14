import json
import csv

inp_file_path = "memory/full_history.json"
out_file_path = "memory/full_history.csv"

# Load JSON safely with UTF-8
with open(inp_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Write CSV safely with UTF-8
with open(out_file_path, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = ["role", "content"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for entry in data:
        writer.writerow(entry)

print("✅ Conversion complete! Saved as 'full_history.csv'")