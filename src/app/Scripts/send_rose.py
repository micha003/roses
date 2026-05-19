import resend
import os
from dotenv import load_dotenv

# load .env from the project src directory (three levels up from this script)
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
)
resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(sender_name, recipient_email, message):
    r = resend.Emails.send(
        {
            "from": "rose@sendroses.de",
            "to": recipient_email,
            "subject": f"{sender_name} sent you a rose",
            "html": f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Valentine Card</title></head><body style="margin:0;padding:0;background-color:#fdf2f5;font-family:Arial,Helvetica,sans-serif;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#fdf2f5;padding:40px 0;"><tr><td align="center"><table role="presentation" width="560" cellspacing="0" cellpadding="0" border="0" style="background:#ffeef3;border-radius:24px;padding:50px 40px;box-shadow:0 4px 20px rgba(0,0,0,0.05);"><tr><td align="center"><div style="font-size:34px;line-height:1.5;color:#7d5663;font-weight:300;letter-spacing:.5px;"><span style="font-weight:bold;">{sender_name}</span> has sent you a rose:</div><div style="font-size:90px;line-height:1;margin:30px 0 35px 0;">🌹</div><div style="font-size:30px;color:#7d5663;font-weight:300;margin-bottom:25px;"></div><div style="background:#fff8fa;border-radius:18px;padding:25px;color:#946f7c;font-size:18px;line-height:1.7;font-style:italic;border:1px solid #ffd9e4;">{message}</div></td></tr></table></td></tr></table></body></html>',
        }
    )


if __name__ == "__main__":
    send_email("Micha", "mirwaldmagnus@gmail.com", "Hey, bist sehr nett :D")
