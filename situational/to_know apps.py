import winapps
import json
from pathlib import Path

# Collect application data
apps_data = []
for app in winapps.list_installed():
    apps_data.append({
        "name": app.name,
        "version": app.version,
        "install_location": str(app.install_location) if app.install_location else "",
        "publisher": app.publisher,
        "uninstall_string": app.uninstall_string
    })

# Save to JSON
output_path = Path("memory/installed_apps.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(apps_data, f, indent=4)

print(f"✅ Saved installed apps to: {output_path.resolve()}")
