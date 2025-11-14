import os
import json

games = []
search_dirs = ["C:"]

for directory in search_dirs:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".exe"):
                games.append({
                    "name": file,
                    "path": os.path.join(root, file)
                })

with open("memory/found_executables.json", "w") as f:
    json.dump(games, f, indent=4)
