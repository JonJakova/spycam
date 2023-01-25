from flask import Flask
import camera_service

app = Flask(__name__)

@app.route("/status")
def camera_status():
    return camera_service.camera_status() and "Camera is running" or "Camera is not running"


@app.route("/start", methods=["POST"])
def start_camera():
    return camera_service.start_camera() and "Camera started" or "Camera is already running"


@app.route("/stop", methods=["POST"])
def stop_camera():
    return camera_service.stop_camera() and "Camera failed to stop" or "Camera stopped"