import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(sender_name, recipient_email, recipient_name, message):
    r = resend.Emails.send(
        {
            "from": "roses@roses.app",
            "to": recipient_email,
            "subject": "Hello World",
            "html": "<p>Congrats on sending your <strong>first email</strong>!</p>",
        }
    )
