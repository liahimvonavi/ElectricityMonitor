import os
import smtplib
from dotenv import load_dotenv

load_dotenv()
# For future notifications still not needed
def send_email():
    with smtplib.SMTP(host="smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=os.getenv("EMAIL"), password=os.getenv("APP_PASSWORD"))
        connection.sendmail(from_addr=os.getenv("EMAIL"),
                            to_addrs=os.getenv("EMAIL"),
                            msg=(
                                f""
                                )
                            )