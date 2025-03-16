from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import tensorflow as tf
from PIL import Image
from keras.applications import ResNet50
from keras.applications.resnet import preprocess_input
import os
from django.shortcuts import render
from keras.preprocessing import image

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model/final_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Load ResNet50 feature extractor
feature_extractor = ResNet50(
    weights="imagenet", include_top=False, pooling="avg")


def test_upload_page(request):
    return render(request, "detect/test_upload.html")


def preprocess_image(image):
    """
    Convert image to a 2048-dimensional feature vector using ResNet50.
    """
    image = image.resize((224, 224))  # Resize to match CNN input
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)  # Shape (1, 224, 224, 3)
    image_array = preprocess_input(image_array)  # Apply ResNet preprocessing

    # Extract features using ResNet50 (outputs (1, 2048))
    features = feature_extractor.predict(image_array)

    return features  # Now matches model input shape (None, 2048)


@csrf_exempt
def predict_skin_disease(request, threshold=85):
    """
    API endpoint to predict skin disease from an uploaded image.
    Returns only the predicted class.
    """
    if request.method == "POST":
        if "image" not in request.FILES:
            return JsonResponse({"error": "No image provided"}, status=400)

        try:
            # Read uploaded image
            uploaded_file = request.FILES["image"]
            image = Image.open(uploaded_file)

            # Convert image to feature vector
            image_features = preprocess_image(image)

            # Predict using trained model
            disease_classes = [
                "Eczema",
                "Melanoma",
                "Atopic Dermatitis",
                "Basal Cell Carcinoma (BCC)",
                "Melanocytic Nevi (NV)",
                "Benign Keratosis-like Lesions (BKL)"
            ]

            # Get predictions from your model
            predictions = model.predict(image_features)
            probabilities = predictions[0] * 100  # Convert to percentage

            # Get highest probability and corresponding class
            max_index = np.argmax(probabilities)
            max_probability = probabilities[max_index]
            predicted_class = disease_classes[max_index]

            if max_probability < threshold:
                print("The model could not confidently identify the disease. Your skin may be healthy or an unrecognized condition probability:", max_probability)
                return JsonResponse({"message": "The model could not confidently identify the disease. Your skin may be healthy or an unrecognized condition.", "probability": f"{max_probability:.2f}%"})
            else:
                # Debugging: Print model output and predicted class
                print("Predicted class index:", max_index)
                print("Predicted class probability:", max_probability)
                print("Predicted class name:", predicted_class)

                # Return the predicted class and probability
                return JsonResponse({"predicted_class": predicted_class, "probability": f"{max_probability:.2f}%"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
