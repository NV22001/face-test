from flask import Flask, render_template, request, jsonify
import threading
import cv2
from deepface import DeepFace
import numpy as np

app = Flask(__name__, static_folder="dumass-project/static", template_folder="dumass-project/templates")

# Initialize video capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# Load the reference image
reference_img_path = "/workspaces/face-test/dumass-project/reference.jpg"
reference_img = cv2.imread(reference_img_path)
if reference_img is None:
    print(f"Error: Could not load reference image from {reference_img_path}.")
    exit()

# Global variables for face match status
face_match = False
lock = threading.Lock()


def check_face(frame):
    global face_match
    try:
        result = DeepFace.verify(frame, reference_img.copy())
        with lock:
            face_match = result['verified']
    except ValueError:
        with lock:
            face_match = False


@app.route("/")
def index():
    """Serve the homepage."""
    return render_template("dumass-project/templates/index.html")


@app.route('/process_frame', methods=['POST'])
def process_frame():
    global face_match

    try:
        if 'frame' not in request.files:
            print("No file part in the request")
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['frame']
        if file.filename == '':
            print("No file selected")
            return jsonify({"error": "No file selected"}), 400

        # Read and decode the image
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if frame is None:
            print("Frame decoding failed")
            return jsonify({"error": "Frame decoding failed"}), 400

        print("Frame received and decoded successfully")

        # Process the frame in a separate thread
        threading.Thread(target=check_face, args=(frame.copy(),)).start()

        with lock:
            print("Current face_match status:", face_match)
            return jsonify({"face_match": face_match})
    except Exception as e:
        print("Error processing the image:", str(e))
        return jsonify({"error": f"Error processing the image: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)