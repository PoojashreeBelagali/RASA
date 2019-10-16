import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def initialize_app(config):
    return SendMail(config)

class SendMail:


    def __init__(self, config):
        self.user_mail = config["user_mail"]
        self.user_password = config["user_password"]

    def send_mail(self, to, content):
        #mail_content = 'Hello,This is a simple mail. There is only text, no attachments are there The mail is sent using Python SMTP library. Thank You'
        # The mail addresses and password
        sender_address = self.user_mail
        sender_pass = self.user_password
        receiver_address = to
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Top 10 resturant for your resturant search'  # The subject line
        # The body and the attachments for the mail
        message.attach(MIMEText(content, 'plain'))
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()


