const video = document.getElementById("video");
const statusText = document.getElementById("status");
const canvas = document.createElement("canvas");
const context = canvas.getContext("2d");

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing the camera:", err);
        statusText.textContent = "Error: Could not access the camera.";
    }
}

function captureFrameAndSend() {
    if (!video.videoWidth || !video.videoHeight) {
        console.error("Video dimensions not yet available.");
        return;
    }

    // Set canvas dimensions to match video dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame to the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert the canvas to a data URL in JPEG format
    canvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append("frame", blob);

        // Send the frame to the backend
        fetch("/process_frame", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Response from backend:", data);
                if (data.face_match) {
                    statusText.textContent = "Status: MATCH!";
                } else {
                    statusText.textContent = "Status: NO MATCH!";
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                statusText.textContent = "Error: Could not process frame.";
            });
    }, "image/jpeg");
}

// Start capturing frames every 2 seconds
setInterval(captureFrameAndSend, 2000);

// Start the camera when the page loads
startCamera();