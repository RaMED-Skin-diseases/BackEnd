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
@permission_classes([IsAuthenticated])
def send_image_to_api(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        temp_image_path = default_storage.save(f"temp/{image.name}", image)

        api_url = os.getenv('TENSORFLOW_URL')
        try:
            with default_storage.open(temp_image_path, "rb") as image_file:
                files = {
                    "file": (image.name, image_file, image.content_type or "application/octet-stream")
                }
                res = requests.post(api_url, files=files)
                if res.status_code != 200:
                    raise ValueError(
                        f"TensorFlow API returned error: {res.text}")

                result = res.json()

        except requests.exceptions.RequestException as e:
            default_storage.delete(temp_image_path)
            return JsonResponse({"error": f"Error communicating with the model: {str(e)}"}, status=500)
        except json.JSONDecodeError:
            default_storage.delete(temp_image_path)
            return JsonResponse({"error": "Model returned an invalid JSON response"}, status=500)
        except ValueError as e:
            default_storage.delete(temp_image_path)
            return JsonResponse({"error": str(e)}, status=500)

        default_storage.delete(temp_image_path)

        # Evaluate model response
        prediction = result.get("class")
        confidence_str = result.get("probability", "0")
        try:
            confidence = float(str(confidence_str).replace('%', '').strip())
        except ValueError:
            confidence = 0.0

        if confidence < 85.0 or not prediction:
            final_result = {
                "message": "The model couldn't detect your disease with sufficient confidence."
            }
        else:
            final_result = {
                "model": "tensorflow",
                "class": prediction,
                "probability": f"{confidence}%",
            }

        # Save diagnosis
        diagnosis = Diagnosis.objects.create(
            user=request.user,
            image=image,
            diagnosis_result=json.dumps(final_result),
        )

        return JsonResponse({
            "status": "success",
            "message": "Diagnosis saved successfully.",
            "diagnosis_id": diagnosis.id,
            "diagnosis_result": final_result,
        })

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
