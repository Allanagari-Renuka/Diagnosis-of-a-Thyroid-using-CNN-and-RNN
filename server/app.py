from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import numpy as np
from werkzeug.utils import secure_filename
import time
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_BUILD = os.path.join(BASE_DIR, "..", "client", "build")

# Flask setup
app = Flask(__name__, static_folder=CLIENT_BUILD, static_url_path="")
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Upload config
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



# MOCK AUTH SYSTEM
users_db = {}


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if email in users_db:
        return jsonify({"error": "Email already registered"}), 409

    users_db[email] = password

    return jsonify({"message": "User created successfully", "token": "mock-token-123"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if email not in users_db or users_db[email] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "token": "mock-token-123"})



# API ENDPOINTS
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {"status": "ok", "model_loaded": False, "message": "Running in mock mode"}
    )


@app.route("/api/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            logger.info(f"File saved at {filepath}")

            time.sleep(2)

            probability = np.random.random()
            diagnosis = (
                "Potential abnormality" if probability >= 0.5 else "Normal"
            )

            return jsonify(
                {
                    "success": True,
                    "probability": float(probability),
                    "diagnosis": diagnosis,
                    "note": "Mock prediction",
                }
            )

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file type"}), 400


@app.route("/api/specialists", methods=["GET"])
def get_specialists():
    specialists = [
        {
            "id": 1,
            "name": "Dr. Anita Sharma",
            "specialty": "Endocrinologist",
            "rating": 4.8,
        },
        {
            "id": 2,
            "name": "Dr. Rajesh Kumar",
            "specialty": "Thyroid Specialist",
            "rating": 4.7,
        },
    ]
    return jsonify(specialists)

# SERVE REACT FRONTEND BUILD
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    file_path = os.path.join(CLIENT_BUILD, path)

    if path != "" and os.path.exists(file_path):
        return send_from_directory(CLIENT_BUILD, path)

    return send_from_directory(CLIENT_BUILD, "index.html")


# MAIN ENTRY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
