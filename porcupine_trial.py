import pvporcupine
from porcupine import Porcupine
import os
from dotenv import load_dotenv

load_dotenv()

porcupine = porcupine.create(
    access_key = os.getenv("PORCUPINE_ACCESS_KEY"),
    keywords = ['picovoice', 'bumblebee']
)

def get_next_audio_frame():
  pass


while True:
  audio_frame = get_next_audio_frame()
  keyword_index = porcupine.process(audio_frame)
  if keyword_index == 0:
      # detected `porcupine`
      print(1)
  elif keyword_index == 1:
      # detected `bumblebee`
      print(2)

porcupine.delete()