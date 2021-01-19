import configparser
import os
import smtplib, ssl
from email.mime.multipart import MIMEMultipart

config = configparser.ConfigParser()
config.read(r"skryptoweProjekt\project\config.ini")

port = config['Mail']['port']
smtp_server = config['Mail'].get('smtp_server', raw=True)
sender_email = config['Mail'].get('sender_email', raw=True)
password = config['Mail'].get('password', raw=True)


def send_mail(email, webpage):
    """
    Sends mail to user about website that went unavailable
    :param email: Email adress
    :param webpage: Webpage that went unavailable
    :return:
    """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)

        message = MIMEMultipart("alternative")
        message["Subject"] = "Your website " + webpage.url + " is down!"
        message["From"] = sender_email
        message["To"] = email

        server.sendmail(sender_email, email, message.as_string())
