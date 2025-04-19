import os
import time
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.utils import CustomObjectScope
from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from train import iou

app = Flask(__name__)

UPLOAD_FOLDER = "uploaded_images/"
RESULTS_FOLDER = "resultant/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

MODEL_PATH = "files/model.h5"

# Load the model with custom objects
with CustomObjectScope({'iou': iou}):
    model = tf.keras.models.load_model(MODEL_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_image(image_path):
    x = cv2.imread(image_path, cv2.IMREAD_COLOR)
    x = cv2.resize(x, (256, 256))  # Resize to the model's input size
    x = x / 255.0  # Normalize the image
    return x

def mask_parse(mask):
    mask = np.squeeze(mask)
    mask = np.stack([mask, mask, mask], axis=-1)  # Stack for 3 channels
    return mask

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Save the uploaded image
        image_data = request.data
        timestamp = int(time.time())
        filename = os.path.join(UPLOAD_FOLDER, f"image_{timestamp}.jpg")
        with open(filename, "wb") as f:
            f.write(image_data)
        
        # Process the image
        x = read_image(filename)
        y_pred = model.predict(np.expand_dims(x, axis=0))[0] > 0.6  # Predict segmentation mask

        # Prepare the result (concatenate the original image and the mask)
        h, w, _ = x.shape
        white_line = np.ones((h, 10, 3)) * 255.0  # White line separator

        all_images = [
            x * 255.0,  # Original image
            white_line,  # White separator
            mask_parse(y_pred) * 255.0  # Predicted segmentation mask
        ]

        result_image = np.concatenate(all_images, axis=1)

        # Save the result
        result_filename = f"segmented_{timestamp}.png"
        result_path = os.path.join(RESULTS_FOLDER, result_filename)
        cv2.imwrite(result_path, result_image)

        return send_from_directory(RESULTS_FOLDER, result_filename)

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)
