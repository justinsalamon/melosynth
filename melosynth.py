# CREATED: 6/13/14 10:57 AM by Justin Salamon <justin.salamon@nyu.edu>

import argparse, os, wave
import numpy as np


def wavwrite(x,filename,fs=44100,N=16):
    '''
    Synthesize signal x into a wavefile on disk. The values of x must be in the
    range [-1,1].

    :parameters:
    - x : numpy.array
    Signal to synthesize.

    - filename: string
    Path of output wavfile.

    - fs : int
    Sampling frequency, by default 44100.

    - N : int
    Bit depth, by default 16.
    '''

    maxVol=2**15-1.0 # maximum amplitude
    x = x * maxVol # scale x
    # convert x to string format expected by wave
    signal = "".join((wave.struct.pack('h', item) for item in x))
    wv = wave.open(filename, 'w')
    nchannels = 1
    sampwidth = N / 8 # in bytes
    framerate = fs
    nframe = 0 # no limit
    comptype = 'NONE'
    compname = 'not compressed'
    wv.setparams((nchannels, sampwidth, framerate, nframe, comptype, compname))
    wv.writeframes(signal)
    wv.close()


def loadmel(inputfile,delimiter=None):
    '''
    Load a pitch (frequency) time series from a file.

    The pitch file must be in the following format:
    Double-column - each line contains two values, separated by ``delimiter``:
    the first contains the timestamp, and the second contains its corresponding
    frequency value in Hz.

    :parameters:
    - inputfile : str
    Path to pitch file

    - delimiter : str
    Column separator. By default, lines will be split by any amount of
    whitespace, unless the file ending is .csv, in which case a comma ','
    is used as the delimiter.

    :returns:
    - times : np.ndarray
    array of timestamps (float)
    - freqs : np.ndarray
    array of corresponding frequency values (float)
    '''
    if os.path.splitext(inputfile)[1] == '.csv':
        delimiter = ','
    try:
        data = np.loadtxt(inputfile,'float','#',delimiter)
    except ValueError:
        raise ValueError('Error: could not load %s, please check if it is in \
        the correct 2 column format' % os.path.basename(inputfile))

    # Make sure the data is in the right format
    data = data.T
    if data.shape[0] != 2:
        raise ValueError('Error: %s should be of dimension (2,x), but is of \
        dimension %s' % (os.path.basename(inputfile),data.shape))
    times = data[0]
    freqs= data[1]
    return times, freqs


def melosynth(inputfile, outputfile, fs, nHarmonics, square, useneg):
    '''
    Load pitch sequence from  a txt/csv file and synthesize it into a .wav

    :parameters:
    - inputfile : str
    Path to input file containing the pitch sequence.

    - outputfile: str
    Path to output wav file. If outputfile is None a file will be
    created with the same path/name as inputfile but ending with ".wav"

    - fs : int
    Sampling frequency for the synthesized file.

    - nHarmonics : int
    Number of harmonics (including the fundamental) to use in the synthesis
    (default is 1). As the number is increased the wave will become more
    sawtooth-like.

    - square : bool
    When set to true, the waveform will converge to a square wave instead of
    a sawtooth as the number of harmonics is increased.

    - useneg : bool
    By default, negative frequency values (unvoiced frames) are synthesized as
    silence. If useneg is set to True, these frames will be synthesized using
    their absolute values (i.e. as voiced frames).
    '''

    # Preprocess input parameters
    fs = int(float(fs))
    nHarmonics = int(nHarmonics)
    if outputfile is None:
        outputfile = inputfile[:-3] + "wav"

    # Load pitch sequence
    print 'Loading data...'
    times, freqs= loadmel(inputfile)

    # Preprocess pitch sequence
    if useneg:
        freqs = np.abs(freqs)
    else:
        freqs[freqs<0] = 0
    # Impute silence if start time > 0
    if times[0] > 0:
        estimated_hop = np.median(np.diff(times))
        prev_time = max(times[0] - estimated_hop, 0)
        times = np.insert(times,0,prev_time)
        freqs = np.insert(freqs,0,0)


    print 'Generating wave...'
    signal = []

    translen = 0.002 # duration (in seconds) for fade in/out and freq interp
    phase = np.zeros(nHarmonics) # start phase for all harmonics
    f_prev = 0 # previous frequency
    t_prev = 0 # previous timestamp
    for t,f in zip(times, freqs):

        # Compute number of samples to synthesize
        nsamples = np.round((t - t_prev) * fs)

        if nsamples > 0:
            # calculate transition length (in samples)
            translen_sm = float(min(np.round(translen*fs),nsamples))

            # Generate frequency series
            freq_series = np.ones(nsamples) * f_prev

            # Interpolate between non-zero frequencies
            if f_prev >  0 and f > 0:
                freq_series += np.minimum(np.arange(nsamples)/translen_sm,1) * \
                               (f - f_prev)
            elif f > 0:
                freq_series = np.ones(nsamples) * f

            # Repeat for each harmonic
            samples = np.zeros(nsamples)
            for h in range(nHarmonics):
                # Determine harmonic num (h+1 for sawtooth, 2h+1 for square)
                hnum = 2*h+1 if square else h+1
                # Compute the phase of each sample
                phasors = 2 * np.pi * (hnum) * freq_series / float(fs)
                phases = phase[h] + np.cumsum(phasors)
                # Compute sample values and add
                samples += np.sin(phases) / (hnum)
                # Update phase
                phase[h] = phases[-1]

            # Fade in/out and silence
            if f_prev == 0 and f > 0:
                samples *= np.minimum(np.arange(nsamples)/translen_sm,1)
            if f_prev > 0 and f == 0:
                samples *= np.maximum(1 - (np.arange(nsamples)/translen_sm),0)
            if f_prev == 0 and f == 0:
                samples *= 0

            # Append samples
            signal.extend(samples)

        t_prev = t
        f_prev = f

    # Normalize signal
    signal = np.asarray(signal)
    signal *= 0.8 / float(np.max(signal))

    print 'Saving wav file...'
    wavwrite(np.asarray(signal),outputfile,fs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthesize pitch sequence.")
    parser.add_argument("inputfile", help="Path to input file containing the \
                        pitch sequence")
    parser.add_argument("--output", help="Path to output wav file. If \
                        not specified a file will be created with the same \
                        path/name as inputfile but ending with \".wav\".")
    parser.add_argument("--fs", default=11025, help="Sampling frequency for the\
                        synthesized file. If not specified the default value \
                        of is 11025 Hz is used.")
    parser.add_argument("--nHarmonics", default=1, help="Number of harmonics \
                        (including the fundamental) to use in the synthesis \
                        (default is 1). As the number is increased the wave \
                        will become more sawtooth-like.")
    parser.add_argument("--square", default = False, dest='square',
                        action='store_const', const=True, help="Converge to \
                        square wave instead of sawtooth as the number of \
                        harmonics is increased.")
    parser.add_argument("--useneg", default = False, dest='useneg',
                        action='store_const', const=True, help="By default, \
                        negative frequency values (unvoiced frames) are \
                        synthesized as silence. Setting the useneg option \
                        will synthesize these frames using their absolute \
                        values (i.e. as voiced frames).")

    args = parser.parse_args()
    if args.inputfile is not None:
        melosynth(args.inputfile, args.output, args.fs, args.nHarmonics,
                  args.square, args.useneg)