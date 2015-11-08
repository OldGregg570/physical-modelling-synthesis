import pyaudio
import numpy as np

p = pyaudio.PyAudio()

RATE, DURATION = 44100, 1.0

def sample_range (duration):
    return np.arange(RATE * duration)

def sin (f):
    return np.sin(2 * np.pi * sample_range(DURATION) * f / RATE)

def hzosc(f):
    return (sin(f)).astype(np.float32)

ostream = p.open(format   = pyaudio.paFloat32,
                 channels = 1,
                 rate     = RATE,
                 output   = True)

ostream.write(0.5 * (hzosc(440.0) + hzosc(880.0)))

ostream.stop_stream()

ostream.close()
p.terminate()
