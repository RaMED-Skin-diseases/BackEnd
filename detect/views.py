import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .models import Diagnosis
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import json
from dotenv import load_dotenv
import os


load_dotenv()


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def send_image_to_api(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Save the uploaded file temporarily
        temp_image_path = default_storage.save(f"temp/{image.name}", image)

        # API endpoint
        api_url = os.getenv('MODEL_URL')

        # Open the saved image file in binary mode
        with default_storage.open(temp_image_path, "rb") as image_file:
            # Adjust the key if the API requires a different one
            files = {"file": image_file}

            # Send request to external API
            response = requests.post(api_url, files=files)

        # Remove the temporary file after sending
        default_storage.delete(temp_image_path)

        # Handle the API response
        try:
            diagnosis_data = response.json()  # Assuming the API returns JSON
            if diagnosis_data:
                # Save the diagnosis to the database with the image
                diagnosis = Diagnosis.objects.create(
                    user=request.user,  # assuming the user is authenticated
                    image=image,  # Save the image uploaded (stored in S3)
                    # Save the diagnosis result as JSON
                    diagnosis_result=json.dumps(diagnosis_data),
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_diagnoses(request):
    diagnoses = Diagnosis.objects.filter(
        user=request.user).order_by('-created_at')
    diagnosis_list = [
        {
            'id': diag.id,
            'diagnosis_result': diag.diagnosis_result,
            'created_at': diag.created_at,
            'image_url': request.build_absolute_uri(diag.image.url) if diag.image else None
        }
        for diag in diagnoses
    ]
    return JsonResponse({'diagnoses': diagnosis_list})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_diagnosis(request, diagnosis_id):
    try:
        # Find the diagnosis by its ID
        diagnosis = Diagnosis.objects.get(id=diagnosis_id)

        # Check if the diagnosis belongs to the current authenticated user
        if diagnosis.user == request.user:
            diagnosis.delete()  # Delete the diagnosis record
            return JsonResponse({"status": "success", "message": "Diagnosis deleted successfully."})
        else:
            return JsonResponse({"error": "You do not have permission to delete this diagnosis."}, status=403)

    except Diagnosis.DoesNotExist:
        return JsonResponse({"error": "Diagnosis not found."}, status=404)
