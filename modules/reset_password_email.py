#!usr/bon/env python3

# import necessary modules
from email import message
import smtplib
from email.message import EmailMessage

def send(email, url):
    message = EmailMessage()
    message["Subject"] = "Shopping website reset password"
    message["From"] = "Manager"
    message["To"] = email

    # Add the add_alternative
    message.add_alternative(
        """
        <!DOCTYPE html>
        <html lang="en-us">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />                                        
        </head>
        <body>
            <p>Click the following hyperlink to reset your password!</p>
            <a href="%s">%s</a>
        </body>
        </html>
        """ % (url, url), subtype="html")
    
    # Send the message via SMTP server.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("","")
        server.send_message(message)