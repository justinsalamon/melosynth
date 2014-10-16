MeloSynth
=========

MeloSynth: synthesize a melody. <br/>
Author: Justin Salamon <http://www.justinsalamon.com> <br/>
Version: 0.1

MeloSynth is a python script to synthesize melodies represented as a sequence of
pitch (frequency) values. It was written to synthesize the output of the [MELODIA Melody Extraction Vamp Plugin](http://mtg.upf.edu/technologies/melodia),
but can be used to synthesize any pitch sequence represented as a two-column txt
or csv file where the first column contains timestamps and the second contains
the corresponding frequency values in Hertz.

Usage
=====
```
usage: melosynth.py [-h] [--output OUTPUT] [--fs FS] [--nHarmonics NHARMONICS]
                    [--square] [--useneg] [--batch]
                    inputfile

positional arguments:
  inputfile             Path to input file containing the pitch sequence

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       Path to output wav file. If not specified a file will
                        be created with the same path/name as inputfile but
                        ending with "_melosynth.wav".
  --fs FS               Sampling frequency for the synthesized file. If not
                        specified the default value of 16000 Hz is used.
  --nHarmonics NHARMONICS
                        Number of harmonics (including the fundamental) to use
                        in the synthesis (default is 1). As the number is
                        increased the wave will become more sawtooth-like.
  --square              Converge to square wave instead of sawtooth as the
                        number of harmonics is increased.
  --useneg              By default, negative frequency values (unvoiced
                        frames) are synthesized as silence. Setting the
                        --useneg option will synthesize these frames using
                        their absolute values (i.e. as voiced frames).
  --batch               Treat inputfile as a folder and batch process every
                        file within this folder that ends with .csv or .txt.
                        If --output is specified it is expected to be a folder
                        too. If --output is not specified, all synthesized
                        files will be saved into the input folder.
```

Examples
========

Basic usage, without any options:
```
>python melosynth.py ~/Documents/daisy3_melodia.csv
```

This will create a file called daisy3_melodia.wav in the same folder as the
input file (~/Documents/) and use all the default parameter values for the
synthesis.

Advanced usage, including options:
```
>python melosynth.py ~/Documents/daisy3_melodia.csv --output ~/Music/mynewfile.wav --fs 44100 --nHarmonics 10 --square --useneg
```

Here we are providing a specified path for the output instead of the default
location. Next we specify the sample rate for the output (44.1 kHz) instead of
the default value of 16000 Hz. Next, we specify the number of harmonics to use
(10) instead of the default value of 1. Normally, as the number of harmonics is
increased the waveform will converge to a sawtooth wave, however, since we
specify the --square option, it will converge to a square wave instead. Finally,
by specifying the --useneg (use negative) option we make the script use the
absolute value of the frequencies so that negative frequencies are not
synthesized as silence (which is the default behaviour).

Batch processing:
```
>python melosynth.py ~/Documents/melodia_pitch/ --output ~/Documents/melodia_synth/ --batch
```

This will batch process all files ending with .txt or .csv in the melodia_pitch
folder, and save the synthesized melodies into the melodia_synth folder. Every
synthesized file will have the same name as its corresponding input file but
with the ending _melosynth.wav.

Installation
============
Simply download the script and run it from your terminal as instructed above. <br/>
Dependencies: python (tested on 2.7) and numpy (<http://www.numpy.org/>).

Melodia users
=============
In order to use this script to synthesize the output of [MELODIA](http://mtg.upf.edu/technologies/melodia), you need to export the melody to a CSV file first. If you are using [Sonic Visualiser](http://www.sonicvisualiser.org/), this is done by selecting the pane with the extracted melody, clicking File -> Export Annotation Layer... and choosing CSV as the file type. You can also obtain the CSV directly (and batch process entire folders of files) by using MELODIA with [Sonic Annotator](http://www.vamp-plugins.org/sonic-annotator/) (see instructions in the README file that comes with MELODIA for this).

License
=======

MeloSynth: synthesize a melody <br/>
Copyright (C) 2014 Justin Salamon.

MeloSynth is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

MeloSynth is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
