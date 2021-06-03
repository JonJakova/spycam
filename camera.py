import cv2
import queue
import threading
import time
import sys
import smtplib
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime



class VideoCapture:

    def __init__(self, name, classifiers):
        self.email_update_interval = 100  # sends an email only once in this time interval (seconds)
        self.sender = MailSender()
        self.classifiers = classifiers
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
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
                gen_frame, will_send = self.get_object(classifier, frame)
                if will_send:
                    self.send_email(gen_frame, will_send)
                    break
                    

    def read(self):
        return self.q.get()

    def get_object(self, classifier, frame):
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

    def send_email(self, frame, send):
        global last_epoch
        try:
            if send and (time.time() - last_epoch) > self.email_update_interval:
                last_epoch = time.time()
                print("Sending email...")
                self.sender.sendEmail(frame)
                print("done!")
        except:
            print("Error sending email: "), sys.exc_info()[0]


class MailSender:

    def __init__(self):
        self.username = config('MAIL_USERNAME')
        self.password = config('MAIL_PASSWORD')
        self.receiver = config("MAIL_RECEIVER")
        self.host = config('MAIL_HOST')
        self.port = config('MAIL_PORT')

    def sendEmail(self, frame=None):
        current_datetime = datetime.datetime.now()
        mail_content = "Movement was detected " + str(current_datetime)

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = self.username
        message['To'] = self.receiver
        message['Subject'] = 'MOVEMENT WAS DETECTED ALARM! TIME:.' + \
            str(current_datetime)  # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        
        if frame is not None:
            # image = MIMEImage(frame, name=current_datetime.microsecond)
            image = MIMEImage(frame)
            image.add_header('Content-ID', '<image1>')
            message.attach(image)
            
        # Create SMTP session for sending the mail
        session = smtplib.SMTP(self.host, self.port)
        session.starttls()  # enable security
        # login with mail_id and password
        session.login(self.username, self.password)
        text = message.as_string()
        session.sendmail(self.username, self.receiver, text)
        session.quit()


object_classifier_facial = cv2.CascadeClassifier("models/facial_recognition_model.xml")  # an opencv classifier
object_classifier_upperbody = cv2.CascadeClassifier("models/upperbody_recognition_model.xml")  # an opencv classifier
object_classifier_fullbody = cv2.CascadeClassifier("models/fullbody_recognition_model.xml")  # an opencv classifier
last_epoch = 0
cap = VideoCapture(0, [object_classifier_facial, object_classifier_upperbody, object_classifier_fullbody])

while True:
    time.sleep(.5)   # simulate time between events
    frame = cap.read()
    cv2.imshow("frame", frame)
    if chr(cv2.waitKey(1) & 255) == 'q':
        break
