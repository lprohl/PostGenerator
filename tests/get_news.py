#pip install currentsapi-python
from currentsapi import CurrentsAPI
from dotenv import load_dotenv
import os

load_dotenv()
api = CurrentsAPI(api_key=os.getenv("CURRENTS_API_KEY"))

#print(api.latest_news())
#print(api.available())
print(api.search(keywords='Iran and Israel', timeout=120))

