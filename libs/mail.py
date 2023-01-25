import smtplib
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime


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
