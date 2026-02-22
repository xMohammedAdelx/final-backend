# apps/patient/services.py
import logging
import requests
import uuid
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def save_dental_image(uploaded_file):
    """
    Save uploaded dental image to uploads/dental/ with a unique filename.
    Returns (saved_path: Path, relative_path: str) e.g. (Path(...), 'dental/uuid.jpg')
    """
    uploads_root = Path(settings.UPLOADS_ROOT)
    dental_dir = uploads_root / "dental"
    dental_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(uploaded_file.name).suffix or ".jpg"
    if not ext.startswith("."):
        ext = "." + ext
    unique_name = f"{uuid.uuid4()}{ext}"
    saved_path = dental_dir / unique_name

    with open(saved_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    relative_path = f"dental/{unique_name}"
    return saved_path, relative_path


def get_ai_prediction(image_file):
    """
    Send image to AI model for prediction.
    Accepts either a file-like object (UploadedFile) or a path (str/Path).
    """
    ai_url = getattr(settings, "AI_MODEL_URL", "http://127.0.0.1:9000/api/v1/predict")

    if isinstance(image_file, (str, Path)):
        path = Path(image_file)
        if not path.exists():
            return {"error": f"File not found: {path}"}
        with open(path, "rb") as f:
            content = f.read()
        filename = path.name
        content_type = "image/jpeg"
        if path.suffix.lower() in (".png",):
            content_type = "image/png"
    else:
        image_file.seek(0)
        content = image_file.read()
        filename = image_file.name
        content_type = image_file.content_type or "image/jpeg"

    files = {"file": (filename, content, content_type)}

    try:
        response = requests.post(ai_url, files=files, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("AI model request failed: %s (URL: %s)", e, ai_url)
        return {"error": str(e)}