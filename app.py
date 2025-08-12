import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY", 'Missing_Key')

print(api_key)
