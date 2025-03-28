import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required

openai.api_key = "your-openai-api-key"

@csrf_exempt  # Disable CSRF for testing (use proper authentication in production)
@login_required  # Ensure only logged-in users can access the chatbot
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            # Call OpenAI's API
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a dermatology AI assistant."},
                          {"role": "user", "content": user_message}]
            )

            bot_reply = response["choices"][0]["message"]["content"]
            return JsonResponse({"reply": bot_reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
