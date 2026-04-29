# CS416-Modem  

## decoder.py  
Bell 103 modem decoder for text messages encoded as audio (answer-side, 300 bits per second, WAV file). 
First, the WAV file is read in and converted from raw PCM samples to floats in the range [-1, 1]. 
Then, the samples are sliced into bit-sized blocks, and the power is measured for every block using 
numpy's dot product correlator. The frequencies are then compared and whichever is louder wins. 
The bits are then grouped into bytes (10 bits long - 1 start, 1 stop, and 8 data bits). Following
8N1: skip the start bit, collect 8 data bits LSB-first, and skip the stop bit. The bytes are then
converted into their ASCII characters and the decoded message is output and written to message.txt.

## Build Instructions/Setup:  
**The following library needs to be installed**:  
numpy  
  
**Can do so with the following command**:  
pip install numpy

**For decoding any .wav file**:  
Drop the .wav file of your choice in the same directory as the decoder.py file   
  
## Running:  

**Basic usage/default message**:  
python decoder.py

**Verbose mode: prints both detector powers and the decoded bit for every bit position (used for debugging)**:  
python decoder.py -v

**Explicit paths and output files**:  
python decoder.py /path/to/message.wav -o decoded.txt

**For command line argument options and usage**:  
python decoder.py --help

# What I Did:  
I created a decoder that takes in a WAV file as input, decodes the audio into ASCII, then 
outputs the decoded personal message, and writes it to a text file.

# How it Went:  
The process went better than I was expecting. The background information and hints were valuable and 
especially helpful here. It was pretty challenging at first, but I found it to be an interesting use 
of math and correspindingly Python's numpy. Additionally, since the signal was pretty perfect (no noise),
there wasn't any extra filtering or windowing that was necessary.

# What is Still to be Done:  
I didn't get around to the extra section of potential things to implement into this program, so I think
those would be the next steps
