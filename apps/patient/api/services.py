# apps/patient/services.py
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def get_ai_prediction(image_file):
    ai_url = getattr(settings, 'AI_MODEL_URL', 'http://127.0.0.1:9000/api/v1/predict')
    
    # Reset file pointer in case it was read before
    image_file.seek(0)
    files = {"file": (image_file.name, image_file.read(), image_file.content_type or "image/jpeg")}
    
    try:
        response = requests.post(ai_url, files=files, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("AI model request failed: %s (URL: %s)", e, ai_url)
        return {"error": str(e)}