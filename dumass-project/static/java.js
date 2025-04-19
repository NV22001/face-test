const canvas = document.createElement("canvas");
const context = canvas.getContext("2d");

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
    const dataUrl = canvas.toDataURL("/workspaces/face-test/dumass-project/reference.jpg");
    const blob = fetch(dataUrl).then((res) => res.blob());

    // Create a FormData object and append the frame
    blob.then((b) => {
        const formData = new FormData();
        formData.append("frame", b);

        // Send the frame to the backend
        fetch("http://127.0.0.1:5000/process_frame", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Response from backend:", data);
                const statusText = document.getElementById("status");
                if (data.face_match) {
                    statusText.textContent = "Status: MATCH!";
                } else {
                    statusText.textContent = "Status: NO MATCH!";
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                const statusText = document.getElementById("status");
                statusText.textContent = "Error: Could not process frame.";
            });
    });
}

// Capture and send frames every 2 seconds
setInterval(captureFrameAndSend, 2000);