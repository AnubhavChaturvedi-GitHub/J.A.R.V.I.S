import pyaudio
import numpy as np
import time
from TextToSpeech.Fast_DF_TTS import speak

def get_mic_health(seconds=5, initial_threshold=500):
    CHUNK = 1024  # Audio chunk size
    FORMAT = pyaudio.paInt16  # 16-bit resolution
    CHANNELS = 1  # Mono audio
    RATE = 44100  # Sampling rate

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print(f"Recording for {seconds} seconds...")
    time.sleep(1)  # Small pause before recording

    # Initialize variables
    sound_count = 0
    total_samples = 0
    noise_floor = 0  # Ambient noise level
    clipping_count = 0
    signal_sum = 0  # Sum of sound levels
    noise_sum = 0  # Sum of background noise levels (below threshold)
    freq_analysis = []  # Frequency analysis data

    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        volume = np.linalg.norm(data)
        
        # Frequency analysis (FFT)
        freqs = np.fft.fftfreq(len(data))
        fft_spectrum = np.abs(np.fft.fft(data))
        freq_analysis.append(fft_spectrum)

        # Update ambient noise level dynamically
        noise_floor = max(noise_floor, np.mean(np.abs(data)) * 1.5)

        # Dynamic threshold based on ambient noise
        dynamic_threshold = max(initial_threshold, noise_floor)

        # Check for sound detection
        if volume > dynamic_threshold:  # Sound detected
            sound_count += 1
            signal_sum += volume
        else:  # No sound detected (background noise)
            noise_sum += volume

        # Detect clipping (when the sound is too loud for the mic)
        if np.max(np.abs(data)) >= 32767:
            clipping_count += 1

        total_samples += 1

    # Calculate metrics
    mic_health = (sound_count / total_samples) * 100
    avg_signal = signal_sum / max(1, sound_count)
    avg_noise = noise_sum / max(1, (total_samples - sound_count))
    snr = 10 * np.log10(avg_signal / max(1, avg_noise))  # Signal-to-Noise Ratio
    avg_clipping = (clipping_count / total_samples) * 100

    # Frequency analysis (average frequencies captured)
    avg_fft_spectrum = np.mean(freq_analysis, axis=0)
    freq_range_coverage = np.mean(avg_fft_spectrum > np.median(avg_fft_spectrum)) * 100

    # Close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Output advanced health metrics
    health_report = {
        'Microphone Health (%)': mic_health,
        'Average Signal-to-Noise Ratio (dB)': snr,
        'Clipping Percentage (%)': avg_clipping,
        'Frequency Range Coverage (%)': freq_range_coverage
    }

    return health_report

def mike_health():
    health_metrics = get_mic_health(seconds=5)
    for metric, value in health_metrics.items():
        speak(f"{metric}: {value:.2f}")
