import pvporcupine
import pyaudio
import struct

porcupine = pvporcupine.create(
    access_key='/PQM3XlciijjpuL4kTKrQLdXpW0EuR4/kSe2W8JeB980OoAreHqJWg==',
    keyword_paths=['/home/epklein/Documents/dev/bu/EC463/pv/Take-up_en_linux_v2_1_0.ppn']
)

audio = pyaudio.PyAudio()

audio_stream = audio.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("Listening for wake words...")

while True:
    frame = audio_stream.read(porcupine.frame_length)
    frame = struct.unpack_from("h" * porcupine.frame_length, frame)
    word = porcupine.process(frame)
    if word == 0:
        print("Wake word detected.")

