# CREATED: 6/13/14 10:57 AM by Justin Salamon <justin.salamon@nyu.edu>

import argparse, os, wave
import numpy as np

_translen = 0.002 # in seconds


def wavwrite(x,filename,fs=44100,N=16):
    '''
    Synthesize signal into a wavefile on disk

    :parameters:
    - x : numpy.array
    Signal to synthesize. 1 column for mono, 2 columns for stereo

    - filename: string
    Path of output wavfile

    - fs : int
    Sampling frequency, by default 44100

    - N : int
    Bit depth, by default 16
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
    Load a pitch time series from a file.

    The pitch file must be of the following format:
    - Double-column.  Each line contains two values, separated by ``delimiter``: the
    first contains the timestamp, and the second contains its corresponding
    numeric value.

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


def melosynth(inputfile, outputfile, useneg, fs):
    '''
    TODO
    '''
    if fs is None:
        fs = 11025
    if outputfile is None:
        outputfile = inputfile[:-3] + "wav"

    # Load pitch sequence
    print 'Loading data...'
    times, freqs= loadmel(inputfile)
    if useneg:
        freqs = np.abs(freqs)
    else:
        freqs[freqs<0] = 0

    print 'Generating wave...'
    signal = []

    phase = 0
    f_prev = 0
    t_prev = 0
    for t,f in zip(times, freqs):

        # Compute number of samples to synthesize
        nsamples = np.round((t - t_prev) * fs)

        if nsamples > 0:
            # Generate interpolated frequency series
            freq_series = np.ones(nsamples) * f_prev
            freq_series += np.minimum(np.arange(nsamples)/float(min(np.round(_translen*fs),nsamples)),1) * (f - f_prev)
            # Compute the phase of each sample
            phasors = 2 * np.pi * freq_series / float(fs)
            phases = phase + np.cumsum(phasors)
            # Compute sample values
            samples = 0.5 * np.cos(phases)
            # Update phase
            phase = phases[-1]
            # Append samples
            signal.extend(samples)

        t_prev = t
        f_prev = f

    print 'Saving wav file...'
    wavwrite(np.asarray(signal),outputfile,fs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthesize pitch sequence")
    parser.add_argument("inputfile", help="Path to file with pitch values")
    parser.add_argument("--outputfile", help="Path to output file (wav)")
    parser.add_argument("--useneg", dest='useneg', action='store_const', const=True, help="Synthesize negative values (unvoiced frames)")
    parser.add_argument("--fs", help="Specify the sampling frequency for the output (default is 11025 Hz)")

    args = parser.parse_args()
    if args.inputfile is not None:
        melosynth(args.inputfile, args.outputfile, args.useneg, args.fs)