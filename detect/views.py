import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .models import Diagnosis

@csrf_exempt  # Disable CSRF for testing; remove in production or use proper authentication
def send_image_to_api(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Save the uploaded file temporarily
        temp_image_path = default_storage.save(f"temp/{image.name}", image)

        # API endpoint
        api_url = "https://deployment-production-c256.up.railway.app/predict/"

        # Open the saved image file in binary mode
        with default_storage.open(temp_image_path, "rb") as image_file:
            files = {"file": image_file}  # Adjust the key if the API requires a different one

            # Send request to external API
            response = requests.post(api_url, files=files)

        # Remove the temporary file after sending
        default_storage.delete(temp_image_path)

        # Return the API response
        try:
            return JsonResponse(response.json(), safe=False)
        except requests.exceptions.JSONDecodeError:
            return JsonResponse({"error": "Invalid response from API"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt  # Disable CSRF for testing; remove in production or use proper authentication
def send_image_to_api(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Save the uploaded file temporarily
        temp_image_path = default_storage.save(f"temp/{image.name}", image)

        # API endpoint
        api_url = "https://deployment-production-c256.up.railway.app/predict/"

        # Open the saved image file in binary mode
        with default_storage.open(temp_image_path, "rb") as image_file:
            files = {"file": image_file}  # Adjust the key if the API requires a different one

            # Send request to external API
            response = requests.post(api_url, files=files)

        # Remove the temporary file after sending
        default_storage.delete(temp_image_path)

        # Handle the API response
        try:
            diagnosis_data = response.json()  # Assuming the API returns JSON
            if diagnosis_data:
                # Save the diagnosis to the database
                diagnosis = Diagnosis.objects.create(
                    user=request.user,  # assuming the user is authenticated
                    image=image,  # Save the image uploaded
                    diagnosis_result=json.dumps(diagnosis_data),  # Save the diagnosis result as JSON
                )

                return JsonResponse({
                    "status": "success",
                    "message": "Diagnosis saved successfully.",
                    "diagnosis_id": diagnosis.id,
                    "diagnosis_result": diagnosis_data,
                })
            else:
                return JsonResponse({"error": "No diagnosis result found"}, status=500)

        except requests.exceptions.JSONDecodeError:
            return JsonResponse({"error": "Invalid response from API"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)