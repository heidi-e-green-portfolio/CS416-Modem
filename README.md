# CS416-Modem  

## decoder.py  
Decodes a Bell 103 (answer-side, 300 baud, 8N1) WAV file. Outputs the decoded personal message to a .txt file


## Build Instructions/Setup  
**The following library needs to be installed**:  
numpy  
  
Drop .wav file in the same directory as decoder.py  
  
## Running  

**Basic usage**:  
python decoder.py

**Verbose: prints both detector powers and the decoded bit for every bit position**:  
python decoder.py -v

**Explicit paths**:  
python decoder.py /path/to/message.wav -o decoded.txt

**For command line argument options and usage**:  
python decoder.py -help

## Reflection  
**What I Did:**  

**How it Went:**  

**What is Still to be Done:**  
The extra section of stuff to implement
