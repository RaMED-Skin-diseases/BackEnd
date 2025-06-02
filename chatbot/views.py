import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from os import getenv
from dotenv import load_dotenv


# Optional: Better to load the key from environment variables for security
load_dotenv()  # Load environment variables from .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-xxxxxxx")  # fallback in dev

@csrf_exempt
def chatbot_reply(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            user_message = body.get("message")

            if not user_message:
                return JsonResponse({"error": "No message provided."}, status=400)

            # OpenRouter API info
            url = "https://openrouter.ai/api/v1/chat/completions"
            model = "deepseek/deepseek-r1:free"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://skinwise-derma.com",  # Your website
                "X-Title": "Skinwise Derma",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No reply.")
                return JsonResponse({"reply": reply})
            else:
                return JsonResponse({"error": "API request failed.", "details": response.text}, status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method."}, status=405)
