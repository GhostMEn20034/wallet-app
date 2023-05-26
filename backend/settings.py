from dotenv import load_dotenv
import os

load_dotenv('.env')

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SERVICE_SID = os.getenv("SERVICE_SID")
SERVICE_SID_RESET_PWD = os.getenv("SERVICE_SID_RESET_PWD")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
