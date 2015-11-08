import sys
import pyaudio
import numpy as np

p           = pyaudio.PyAudio()
F           = pyaudio.paFloat32
R, D        = 44100, 3.0

def parse_data_table(data_file):
    # Read each line in the file
    read_data = lambda f: [parse(line.split()) for line in f.readlines()]

    # Parses mode frequency and the length of its participatrion vector
    parse = lambda l: (str(l[2]), vlen(l[4:]))

    # Calculate the length of a 3D vector
    vlen = lambda v: (sqfl(v[0]) + sqfl(v[1]) + sqfl(v[2])) ** 0.5

    # Parses input as a float and squares it
    sqfl = lambda f: float(f) ** 2

    ## Parse the data table
    with open(data_file) as f:
        data = read_data(f)

    # Calculate the normalization factor
    n = 1 / sum([float(k[1]) for k in data])

    # Produces a list of frequency / loudness pairs
    return [(d[0], str('{:.20f}'.format(float(d[1]) * n)) ) for d in data]


def output_note(timbre):
    # Calculates a sine waveform for the sample rate
    sin = lambda f: np.sin(2 * np.pi * np.arange(R * D) * f / R)

    # Returns a sine osc
    hzosc = lambda f: (sin(f)).astype(np.float32)

    # Set up the audio output stream
    ostream = p.open(format = F, channels = 1, rate = R, output = True)

    # Build the waveform from the table harmonics
    waveform = 0.0
    for harmonic in timbre:
        waveform += (float(harmonic[1]) * hzosc(float(harmonic[0])))

    # Output the sound
    ostream.write(waveform)

    # Cleanup
    ostream.stop_stream()
    ostream.close()
    p.terminate()


def main(argv):
    timbre = parse_data_table(argv[1])
    output_note(timbre)


if __name__ == "__main__":
    main(sys.argv)
