from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import hashlib
import os
import urllib.error
import urllib.request
from pathlib import Path
from feedback_db import FeedbackDB
from hf_client import get_hf_client
from cyber_dna_engine import CyberDNAEngine
from redteam_engine import RedTeamEngine

try:
    from huggingface_hub import InferenceClient
except ImportError:  # huggingface_hub is optional but recommended
    InferenceClient = None

app = Flask(__name__)
CORS(app)

# Initialize intelligent engines
feedback_db = FeedbackDB()
hf_client_new = get_hf_client()  # Our new unified client
cyber_dna = CyberDNAEngine()
redteam = RedTeamEngine()

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



@app.route("/detect-image", methods=["POST"])
def detect_image():
    """
    Hybrid AI image detection endpoint
    Priority: HF Primary → CyberDNA → RedTeam
    """
    data = request.json or {}
    user_ip = request.remote_addr

    image_bytes, image_id, reference = _load_image_bytes(data)
    if not image_bytes:
        return jsonify({"error": "image_base64 or image_url is required"}), 400

    # === STEP 1: Try New HF Client First (Primary Intelligence) ===
    hf_result_new = hf_client_new.classify_image(image_bytes)
    
    # === STEP 2: Fallback to InferenceClient (if new client fails) ===
    if not hf_result_new:
        hf_result_old = hf_classify_image(image_bytes) if hf_client else None
    else:
        hf_result_old = None
    
    # === STEP 3: Determine Primary Result (HF only) ===
    if hf_result_new:
        # New HF client success - use as primary
        is_fake = bool(hf_result_new["is_fake"])
        prob = float(hf_result_new["confidence"])
        source = "huggingface"
        primary_label = hf_result_new.get("label", "unknown")
        hf_result = hf_result_new
    elif hf_result_old:
        # Old HF client success - use as primary
        is_fake = bool(hf_result_old["is_fake"])
        prob = float(hf_result_old["score"])
        source = "huggingface_legacy"
        primary_label = hf_result_old.get("label", "unknown")
        hf_result = hf_result_old
    else:
        return jsonify({"error": "Image scanning requires Hugging Face service"}), 503

    # === STEP 5: Build Base Scan Result ===
    scan_result = {
        "is_fake": is_fake,
        "score": prob,
        "label": primary_label,
        "image_id": image_id
    }

    # === STEP 6: CyberDNA Analysis (Always Run) ===
    try:
        cyber_dna_result = cyber_dna.generate_dna(
            content=f"image:{image_id}",
            content_type="image",
            scan_result=scan_result,
            redteam_result=None
        )
    except Exception as e:
        cyber_dna_result = None
        print(f"CyberDNA error: {e}")

    # === STEP 7: RedTeam Analysis (Always Run) ===
    try:
        redteam_result = redteam.analyze_image(scan_result)
    except Exception as e:
        redteam_result = None
        print(f"RedTeam error: {e}")

    # === STEP 8: Generate explanations ===
    explanations = []
    if is_fake:
        explanations.append(f"AI detected as {primary_label} with {prob*100:.1f}% confidence")
        if prob > 0.8:
            explanations.append("High confidence deepfake/synthetic detection")
        if "deepfake" in primary_label.lower():
            explanations.append("Potential identity manipulation detected")
    else:
        explanations.append("Image appears authentic")
        explanations.append("No synthetic patterns detected")
    
    # === STEP 9: Store in Feedback Database ===
    feedback_db.add_image_prediction(
        image_id,
        is_fake,
        float(prob),
        user_ip,
        source=source,
        reference=reference,
    )

    # === STEP 10: Build Hybrid Response ===
    response = {
        "image_id": image_id,
        "reference": reference,
        "is_fake": bool(is_fake),
        "confidence": round(prob, 3),
        "risk_level": "High Risk" if is_fake and prob > 0.7 else "Medium Risk" if is_fake else "Low Risk",
        "explanation": explanations,
        "source": source,
        "architecture": "hybrid_ai",

        # Hugging Face Primary Results
        "hf_primary": {
            "available": hf_result is not None,
            "is_fake": hf_result.get("is_fake") if hf_result else None,
            "confidence": round(hf_result.get("score", hf_result.get("confidence", 0)), 3) if hf_result else None,
            "label": hf_result.get("label") if hf_result else None,
            "model": hf_client_new.image_model if hf_result_new else HF_IMAGE_MODEL if hf_result else None
        } if hf_result else {
            "available": False,
            "reason": "API unavailable or timeout"
        },

        # CyberDNA Fingerprint
        "cyber_dna": cyber_dna_result if cyber_dna_result else {
            "available": False,
            "reason": "Analysis failed"
        },

        # RedTeam Intelligence
        "redteam": redteam_result if redteam_result else {
            "available": False,
            "reason": "Analysis failed"
        },

        "note": "Hybrid AI: HF primary + CyberDNA + RedTeam"
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
