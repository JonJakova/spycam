import cv2
import queue
import threading
import time
import sys
from decouple import config
from libs.mail import MailSender
import libs.local_persistency as local_persistency

last_epoch_mailing = 0

class VideoCapture:

    def __init__(self, name, classifiers):
        # sends an email only once in this time interval (seconds)
        self.email_update_interval = int(config('EMAILING_INTERVAL'))
        self.sender = MailSender()
        self.persistency = local_persistency.Persistency()
        self.classifiers = classifiers
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def read(self):
        return self.q.get()

    def status(self) -> bool:
        return self.t.is_alive()

    def end(self) -> None:
        self.cap.release()
        cv2.destroyAllWindows()
        self.t.join()

    def _reader(self):  # read frames as soon as they are available, keeping only most recent one
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)
            for classifier in self.classifiers:
                gen_frame, will_send = self._get_object(classifier, frame)
                if will_send:
                    self._send_email(gen_frame, will_send)
                    self.persistency.save_image(
                        self._get_image_name(), gen_frame)
                    break

    def _get_object(self, classifier, frame):
        found_objects = False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(objects) > 0:
            found_objects = True

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)

    def _send_email(self, frame, send):
        global last_epoch_mailing
        try:
            if send and (time.time() - last_epoch_mailing) > self.email_update_interval:
                last_epoch_mailing = time.time()
                print("Sending email...")
                self.sender.sendEmail(frame)
                print("done!")
        except:
            print("Error sending email: "), sys.exc_info()[0]

    def _get_image_name(self):
        return 'image_' + str(time.time()) + '.jpg'
