# Imports
import argparse
import wave
import numpy as np

# Constants, frequencies are in Hz (mark - 1 bit, space - 0 bit)
MARK_FREQ = 2225
SPACE_FREQ = 2025
# 300 bits per second
BAUD = 300
# 8 data bits plus one start and one stop
BITS_PER_BYTE = 10

def read_wav(path: str) -> tuple[np.ndarray, int]:
    """
    Reads the wav file and gets its attributes. Returns its samples as a float32
    numpy array in range -1..1, and the sampling frequency in Hz.
    """
    with wave.open(path, "rb") as wf:
        # Sampling frequency
        fs = wf.getframerate()
        # Number of channels
        n_channels = wf.getnchannels()
        # Sample width - bytes per sample
        sample_width = wf.getsampwidth()
        # Number of audio frames
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sample_width == 2:
        # 16-bit signed Pulse-Code Modulation, divide by 32768 to get -1..1
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 1:
        # 8-bit unsigned Pulse-Code Modulation, first center on 0 then divide by 128
        samples = (np.frombuffer(raw, dtype=np.unit8).astype(np.float32) - 128) / 128.0
    else:
        raise ValueError(f"Error: unsupported sample width of {sample_width} bytes")
    
    # If there's multiple channels, use the left channel only
    if n_channels > 1:
        samples = samples[::n_channels]
    
    return samples, fs

def make_reference(N: int, freq: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Creates and returns cosine and sine reference arrays for the tone power detector.
    The arrays are of length N: the number of samples per bit/block size
    """
    angles = 2.0 * np.pi * freq * np.arange(N) / fs
    return np.cos(angles), np.sin(angles)

def tone_power(block: np.ndarray, cos_ref: np.ndarray, sin_ref: np.ndarray) -> float:
    """
    Measures the power of a block (a bit's worth) of samples at the target frequency 
    using numpy's dot, and returns the power at the reference frequency.
    """
    # In-phase component
    I = np.dot(block, cos_ref)
    # Quadrature component
    Q = np.dot(block, sin_ref)
    # Power = squared magnitude
    return (I * I) + (Q * Q)

def decode(samples: np.ndarray, fs: float, verbose: bool = False) -> str:
    """
    Does the decoding work - turns the bitstream into an ASCII string.
    """
    # 160 at 48 kHz
    samples_per_bit = int(round(fs / BAUD))
    # 1600 at 48 kHz
    samples_per_byte = samples_per_bit * BITS_PER_BYTE

    # Precompute to save time and for efficiency
    cos_mark, sin_mark = make_reference(samples_per_bit, MARK_FREQ, fs)
    cos_space, sin_space = make_reference(samples_per_bit, SPACE_FREQ, fs)

    # Total number of bytes in the file
    n_bytes = len(samples) // samples_per_byte

    message = []

    for byte_index in range(n_bytes):
        byte_start = byte_index * samples_per_byte
        # Accumulator for the data bits
        byte_value = 0

        if verbose:
            print(f"\nByte {byte_index} (offset {byte_start}):")

        for bit_position in range(BITS_PER_BYTE):
            bit_start = byte_start + (bit_position * samples_per_bit)
            block = samples[bit_start : bit_start + samples_per_bit]

            # If there's an incomplete block at end of file
            if len(block) < samples_per_bit:
                break

            # Determine which is bigger/louder by comparing tone power at mark (2225 Hz) and space (2025 Hz)
            power_mark = tone_power(block, cos_mark, sin_mark)
            power_space = tone_power(block, cos_space, sin_space)

            bit = 1 if power_mark > power_space else 0

            if verbose:
                label = ("START" if bit_position == 0
                        else "STOP " if bit_position == 9
                        else f"D{bit_position-1}   ")
                print(f"    bit {bit_position} ({label}):   "
                    f"mark ={power_mark:7.1f}   space ={power_space:7.1f} -> {bit}")

            # Skip start and stop bits at positions 0 and 9
            if 1 <= bit_position <= 8:
                data_bit = bit_position - 1
                # Least Significant Bit first
                byte_value |= (bit << data_bit)

        # Convert the byte into it's respective ASCII character
        message.append(chr(byte_value))
    
    return "".join(message)

def main():
    parser = argparse.ArgumentParser(description="Decode a Bell 103 (answer-side, 300 baud, 8N1) WAV file.")
    parser.add_argument("wav", nargs="?", default="message.wav",
                        help="Input WAV file. The default is: message.wav")
    parser.add_argument("-o", "--output", default="message.txt",
                        help="Output text file. The default is: message.txt")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print per-bit detector outputs")
    args = parser.parse_args()

    # Sanity-check for detector before decoding
    print(f"\nReading {args.wav}...")
    samples, fs = read_wav(args.wav)
    print(f"    Sample rate: {fs} Hz")
    print(f"    Samples: {len(samples)}")
    print(f"    Samples per bit: {int(round(fs / BAUD))} ({BAUD} baud)")
    print(f"    Samples per byte: {int(round(fs / BAUD)) * BITS_PER_BYTE}")
    print(f"    Bytes: {len(samples) // (int(round(fs / BAUD)) * BITS_PER_BYTE)}")

    text = decode(samples, fs, verbose=args.verbose)

    # Output the decoded message
    print(f"\nFinal decoded message:")
    print(text)

    with open(args.output, "w", encoding="utf-8") as f:
        # Write the decoded message into the message.txt file
        f.write(text)
    print(f"\nDecoded message has been saved to {args.output}\n")

if __name__ == "__main__":
    main()
