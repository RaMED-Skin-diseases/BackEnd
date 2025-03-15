from tensorflow.python.keras.models import load_model
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model/final_model.h5")

def get_model():
    if not hasattr(get_model, "model"):
        get_model.model = load_model(MODEL_PATH)  # Load only once when called
    return get_model.model
