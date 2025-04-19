from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import cv2
from deepface import DeepFace
import os
import numpy as np 

from flask import Flask

app = Flask(__name__, static_folder="static", template_folder="templates")

# Initialize video capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# Load the reference image
reference_img_path = "/workspaces/face-test/dumass-project/static/images/reference.jpg"
reference_img = cv2.imread(reference_img_path)
if reference_img is None:
    print(f"Error: Could not load reference image from {reference_img_path}.")
    exit()
    print(f"Reference image loaded successfully: {reference_img_path}")

# Global variables for face match status
face_match = False
counter = 0
lock = threading.Lock()


def check_face(frame):
    global face_match
    try:
        result = DeepFace.verify(frame, reference_img.copy())
        print("DeepFace result:", result)  # Debugging output
        with lock:
            face_match = result['verified']
    except ValueError as e:
        print("DeepFace error:", e)  # Debugging error
        with lock:
            face_match = False


@app.route("/")
def index():
    """Serve the homepage."""
    return render_template("index.html")


@app.route('/process_frame', methods=['POST'])
def process_frame():
    """
    Process a frame sent from the frontend and return the face match status.
    """
    global face_match
    file = request.files["frame"]
    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Process the frame in a separate thread
    threading.Thread(target=check_face, args=(frame.copy(),)).start()

    # Return the current face match status
    with lock:
        return jsonify({"face_match": face_match})


@app.route('/stop', methods=['POST'])
def stop_recognition():
    """
    Stop the face recognition process and release resources.
    """
    cap.release()
    cv2.destroyAllWindows()
    return jsonify({"status": "Face recognition stopped."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)