import cv2
import queue
import threading
import time
import sys
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime


class VideoCapture:

    def __init__(self, name, classifier):
        self.last_epoch = 0
        self.email_update_interval = 600  # sends an email only once in this time interval
        self.sender = MailSender()
        self.classifier = classifier
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
            gen_frame, will_send = self.get_object(self.classifier, frame)
            self.send_email(gen_frame, will_send)

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
                # sendEmail(frame)
                # self.send_email()
                print("done!")
        except:
            print("Error sending email: "), sys.exc_info()[0]


class MailSender:

    def sendEmail():
        current_datetime = datetime.datetime.now()
        mail_content = "Movement was detected " + str(current_datetime)

        # IF USING gmail it requires a configuration to allow those certain apps to login
        # The mail addresses and password
        sender_address = 'marinmitrovic97@gmail.com'
        sender_pass = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
        receiver_address = 'marinmitrovic97@gmail.com'
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'MOVEMENT WAS DETECTED ALARM! TIME:.' + \
            str(current_datetime)  # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        # login with mail_id and password
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')


object_classifier = cv2.CascadeClassifier(
    "models/fullbody_recognition_model.xml")  # an opencv classifier
last_epoch = 0
cap = VideoCapture(0, object_classifier)

while True:
    time.sleep(.5)   # simulate time between events
    frame = cap.read()
    cv2.imshow("frame", frame)
    if chr(cv2.waitKey(1) & 255) == 'q':
        break
