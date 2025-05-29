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

        api_url_1 = os.getenv('PYTORCH_URL')
        api_url_2 = os.getenv('TENSORFLOW_URL')

        responses = {}

        try:
            with default_storage.open(temp_image_path, "rb") as image_file1:
                files1 = {
                    "file": (image.name, image_file1, image.content_type or "application/octet-stream")
                }
                res1 = requests.post(api_url_1, files=files1)
                responses["model1"] = res1.json() if res1.status_code == 200 else {
                    "error": res1.text}

            with default_storage.open(temp_image_path, "rb") as image_file2:
                files2 = {"file": image_file2}
                res2 = requests.post(api_url_2, files=files2)
                responses["model2"] = res2.json() if res2.status_code == 200 else {
                    "error": res2.text}

        except requests.exceptions.RequestException as e:
            default_storage.delete(temp_image_path)
            return JsonResponse({"error": f"Error communicating with models: {str(e)}"}, status=500)
        except json.JSONDecodeError:
            default_storage.delete(temp_image_path)
            return JsonResponse({"error": "One of the models returned an invalid JSON response"}, status=500)

        default_storage.delete(temp_image_path)
        # Extract predictions and confidences from responses if available
        best_prediction = None
        best_confidence = 0.0
        best_model = None

        for model_key in ["model1", "model2"]:
            result = responses.get(model_key)
            if result and "probability" in result and "class" in result:
                try:
                    # Clean and convert probability string to float
                    confidence_str = result["probability"]
                    confidence = float(
                        str(confidence_str).replace('%', '').strip())

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_prediction = result["class"]
                        best_model = model_key
                except ValueError:
                    continue

        # Apply threshold check
        if best_confidence < 85.0 or best_prediction is None:
            final_result = {
                "message": "The model couldn't detect your disease with sufficient confidence."
            }
        else:
            final_result = {
                "model": best_model,
                "class": best_prediction,
                "probability": f"{best_confidence}%",
            }

        # Save the diagnosis with full results (optional, you can decide what to save)
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
