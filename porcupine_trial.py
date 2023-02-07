import pvporcupine
import os
from dotenv import load_dotenv

load_dotenv()

# Porcupine access key
access_key = os.getenv("PORCUPINE_ACCESS_KEY")
print(access_key)

