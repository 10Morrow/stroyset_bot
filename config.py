from dotenv import load_dotenv
import os

load_dotenv()

# bot connect information
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# data for connecting to payment system api
PAY_SYS_NAME = os.environ.get("PAY_SYS_NAME")
PAY_SYS_PASS = os.environ.get("PAY_SYS_PASS")

# website api token
API_TOKEN = os.environ.get("API_TOKEN")
