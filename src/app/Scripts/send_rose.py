import resend
import os
from dotenv import load_dotenv

# load .env from the project src directory (three levels up from this script)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
resend.api_key = os.getenv("RESEND_API_KEY")
print(f"RESEND_API_KEY: {resend.api_key}")  # Debugging line


def send_email(sender_name, recipient_email):
    r = resend.Emails.send(
        {
            "from": "roses@sendroses.de",
            "to": recipient_email,
            "subject": "Hello World",
            "html": "<p>Congrats on sending your <strong>first email</strong>!</p>",
        }
    )


if __name__ == "__main__":
    pass
