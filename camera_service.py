from libs.camera import VideoCapture
import cv2


camera: VideoCapture = None


def camera_status() -> bool:
    return camera is not None and camera.status()


def start_camera() -> bool:
    global camera
    if camera is not None:
        return False
    camera = VideoCapture(0, [object_classifier_facial,
                              object_classifier_upperbody, object_classifier_fullbody])
    return camera_status()


def stop_camera() -> bool:
    global camera
    if camera is not None:
        camera.end()
        camera = None
    return camera_status()


object_classifier_facial = cv2.CascadeClassifier(
    "models/facial_recognition_model.xml")  # an opencv classifier
object_classifier_upperbody = cv2.CascadeClassifier(
    "models/upperbody_recognition_model.xml")  # an opencv classifier
object_classifier_fullbody = cv2.CascadeClassifier(
    "models/fullbody_recognition_model.xml")  # an opencv classifier
