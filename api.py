from flask import Flask, Response
import camera_service

app = Flask(__name__)

@app.route("/camera/status")
def camera_status():
    return camera_service.camera_status() and Response("Camera is running") or Response("Camera is not running")


@app.route("/camera/start", methods=["POST"])
def start_camera():
    return camera_service.start_camera() and Response("Camera started") or Response("Camera is already running")


@app.route("/camera/stop", methods=["POST"])
def stop_camera():
    return camera_service.stop_camera() and Response("Camera failed to stop") or Response("Camera stopped")