import requests, os

def solve_captcha(image_base64):
    url = "https://api.capsolver.com/solve"
    payload = {
        "clientKey": os.getenv("CAPSOLVER_API_KEY"),
        "task": {
            "type": "ImageToTextTask",
            "body": image_base64
        }
    }
    response = requests.post(url, json=payload).json()
    return response.get("solution", {}).get("text", "")

