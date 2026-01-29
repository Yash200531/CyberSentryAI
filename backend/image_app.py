from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import hashlib
import os
import pickle
import urllib.error
import urllib.request
from pathlib import Path
from feedback_db import FeedbackDB

try:
    from huggingface_hub import InferenceClient
except ImportError:  # huggingface_hub is optional but recommended
    InferenceClient = None

app = Flask(__name__)
CORS(app)

feedback_db = FeedbackDB()

HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "prithivMLmods/DeepFake-Detection")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_TIMEOUT = float(os.getenv("HF_TIMEOUT", "20"))

hf_client = None
if HF_API_TOKEN and InferenceClient:
    try:
        hf_client = InferenceClient(
            model=HF_IMAGE_MODEL,
            token=HF_API_TOKEN,
            timeout=HF_TIMEOUT,
        )
        app.logger.info("HF Inference client ready for %s", HF_IMAGE_MODEL)
    except Exception:
        hf_client = None
        app.logger.warning("Failed to initialize HF Inference client", exc_info=True)

IMAGE_STORAGE_DIR = Path("feedback_data/image_samples")
IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

LOCAL_IMAGE_MODEL_PATH = Path("models/image_deepfake_model.pkl")
LOCAL_IMAGE_MODEL = None


def _get_local_model():
    global LOCAL_IMAGE_MODEL
    if LOCAL_IMAGE_MODEL is None and LOCAL_IMAGE_MODEL_PATH.exists():
        try:
            with open(LOCAL_IMAGE_MODEL_PATH, "rb") as f:
                LOCAL_IMAGE_MODEL = pickle.load(f)
            app.logger.info("Loaded local image model from %s", LOCAL_IMAGE_MODEL_PATH)
        except Exception:
            LOCAL_IMAGE_MODEL = None
            app.logger.warning("Failed to load local image model", exc_info=True)
    return LOCAL_IMAGE_MODEL


def _guess_extension(image_bytes: bytes) -> str:
    if image_bytes.startswith(b"\x89PNG"):
        return ".png"
    if image_bytes.startswith(b"\xff\xd8"):
        return ".jpg"
    return ".bin"


def _store_image(image_bytes: bytes) -> str:
    image_id = hashlib.sha256(image_bytes).hexdigest()
    ext = _guess_extension(image_bytes)
    file_path = IMAGE_STORAGE_DIR / f"{image_id}{ext}"
    if not file_path.exists():
        file_path.write_bytes(image_bytes)
    return image_id, str(file_path)


def _load_image_bytes(data):
    if "image_base64" in data and data["image_base64"]:
        image_bytes = base64.b64decode(data["image_base64"])
        image_id, reference = _store_image(image_bytes)
        return image_bytes, image_id, reference
    if "image_url" in data and data["image_url"]:
        url = data["image_url"]
        try:
            with urllib.request.urlopen(url, timeout=HF_TIMEOUT) as resp:
                image_bytes = resp.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
            return None, None, None
        image_id, reference = _store_image(image_bytes)
        return image_bytes, image_id, reference
    return None, None, None


def hf_classify_image(image_bytes: bytes):
    if not hf_client:
        return None
    try:
        data = hf_client.image_classification(image_bytes)
    except Exception:
        app.logger.warning("HF image classification failed", exc_info=True)
        return None

    if isinstance(data, list) and data:
        best = max(data, key=lambda item: item.get("score", 0))
        label = str(best.get("label", "")).lower()
        score = float(best.get("score", 0))
        is_fake = any(key in label for key in ("fake", "deepfake", "ai", "synthetic"))
        if any(key in label for key in ("real", "authentic")):
            is_fake = False
        return {"label": label, "score": score, "is_fake": is_fake}

    return None


def local_classify_image(image_bytes: bytes):
    model = _get_local_model()
    if not model:
        return None
    try:
        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba([image_bytes])[0][1])
            return {"is_fake": prob >= 0.5, "score": prob}
        if hasattr(model, "predict"):
            pred = model.predict([image_bytes])[0]
            is_fake = bool(pred)
            return {"is_fake": is_fake, "score": 1.0 if is_fake else 0.0}
    except Exception:
        return None
    return None


@app.route("/detect-image", methods=["POST"])
def detect_image():
    data = request.json or {}
    user_ip = request.remote_addr

    image_bytes, image_id, reference = _load_image_bytes(data)
    if not image_bytes:
        return jsonify({"error": "image_base64 or image_url is required"}), 400

    hf_result = hf_classify_image(image_bytes) if hf_client else None
    local_result = local_classify_image(image_bytes)

    if hf_result:
        is_fake = bool(hf_result["is_fake"])
        prob = float(hf_result["score"])
        source = "huggingface"
    elif local_result:
        is_fake = bool(local_result["is_fake"])
        prob = float(local_result["score"])
        source = "local"
    else:
        return jsonify({"error": "No model available for image detection"}), 503

    feedback_db.add_image_prediction(
        image_id,
        is_fake,
        float(prob),
        user_ip,
        source=source,
        reference=reference,
    )

    response = {
        "image_id": image_id,
        "reference": reference,
        "is_fake": bool(is_fake),
        "confidence": round(prob, 3),
        "risk_level": "High Risk" if is_fake and prob > 0.7 else "Medium Risk" if is_fake else "Low Risk",
        "source": source,
    }

    if hf_result:
        response["hf_primary"] = {
            "is_fake": hf_result["is_fake"],
            "confidence": round(hf_result["score"], 3),
            "label": hf_result["label"],
            "model": HF_IMAGE_MODEL,
        }

    if local_result:
        response["local_verification"] = {
            "is_fake": bool(local_result["is_fake"]),
            "confidence": round(float(local_result["score"]), 3),
        }

    return jsonify(response)


@app.route("/report-image", methods=["POST"])
def report_image():
    data = request.json or {}
    image_id = data.get("image_id", "")
    label = data.get("label", "").lower()  # 'real' or 'fake'
    comment = data.get("comment", "")
    reference = data.get("reference")
    user_ip = request.remote_addr

    if not image_id:
        return jsonify({"error": "image_id is required"}), 400

    if label not in ["real", "fake"]:
        return jsonify({"error": "Label must be 'real' or 'fake'"}), 400

    feedback_db.add_image_report(image_id, label, user_ip, comment, reference=reference)

    return jsonify({
        "success": True,
        "message": "Thank you for your feedback! Your report helps improve our model.",
        "image_id": image_id,
        "reported_as": label,
    })


@app.route("/feedback-stats", methods=["GET"])
def feedback_stats():
    stats = feedback_db.get_stats()
    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
