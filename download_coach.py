import requests
import os

image_url = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
save_path = "static/coach.png"

os.makedirs("static", exist_ok=True)

try:
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    print("Coach image downloaded successfully.")

except Exception as e:
    print("Download failed:", e)