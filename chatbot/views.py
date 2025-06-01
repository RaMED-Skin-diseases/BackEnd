import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-or-xxxxxxx")


@csrf_exempt
def chatbot_reply(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            user_message = body.get("message")

            if not user_message:
                return JsonResponse({"error": "No message provided."}, status=400)

            # Prepare OpenRouter request
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://skinwise.tech",
                "X-Title": "Skinwise",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": user_message}],
                "stream": True
            }

            # Make the request with streaming enabled
            response = requests.post(
                url, headers=headers, json=payload, stream=True)

            def stream_response():
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            data = decoded_line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                parsed = json.loads(data)
                                content = parsed["choices"][0]["delta"].get(
                                    "content", "")
                                yield content
                            except Exception as e:
                                yield f"[ERROR: {str(e)}]"

            return StreamingHttpResponse(stream_response(), content_type="text/plain")

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method."}, status=405)
