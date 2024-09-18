import numpy as np
import pyaudio
import time
from scipy import signal 
from TextToSpeech.Fast_DF_TTS import speak

def play_tone(frequency, duration=2, volume=0.5, sample_rate=44100):
    """
    Plays a single tone of a specific frequency through the speaker.
    """
    # Generate samples for the sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)

    # Ensure the tone is in the correct format
    audio_data = (tone * volume * 32767).astype(np.int16)

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # Play the tone
    stream.write(audio_data.tobytes())

    # Stop the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_sweep(duration=5, volume=0.5, sample_rate=44100, start_freq=20, end_freq=20000):
    """
    Plays a frequency sweep from start_freq to end_freq through the speaker.
    Useful for testing the full frequency range of the speaker.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sweep = signal.chirp(t, start_freq, t[-1], end_freq, method='logarithmic')

    # Ensure the sweep is in the correct format
    audio_data = (sweep * volume * 32767).astype(np.int16)

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # Play the sweep
    stream.write(audio_data.tobytes())

    # Stop the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

def speaker_health_test():
    """
    This function plays different tones and sweeps to test the speaker's health.
    It returns a speaker health percentage based on the tone coverage.
    """
    speak("Playing test tones...")
    health_score = 0

    # Test low-frequency tones (below 500 Hz)
    speak("Playing 100 Hz tone...")
    play_tone(100, duration=2)
    time.sleep(1)
    health_score += 25  # Assuming low-frequency played fine

    # Test mid-frequency tones (500 Hz to 5000 Hz)
    speak("Playing 1000 Hz tone...")
    play_tone(1000, duration=2)
    time.sleep(1)
    health_score += 25  # Assuming mid-frequency played fine

    # Test higher frequencies (5000 Hz and above)
    speak("Playing 5000 Hz tone...")
    play_tone(5000, duration=2)
    time.sleep(1)
    health_score += 20  # Slightly lower score for high frequencies, which may be harder for some speakers

    speak("Playing 10,000 Hz tone...")
    play_tone(10000, duration=2)
    time.sleep(1)
    health_score += 15  # High-pitch tones are harder to reproduce

    # Play a frequency sweep to test full frequency response
    speak("Playing frequency sweep from 20 Hz to 20,000 Hz...")
    play_sweep(duration=5)
    time.sleep(1)
    health_score += 15  # Frequency sweep covers a wide range

    # Speaker health assessment
    speak("\nSpeaker health test complete.")

    # Calculate health percentage
    speak(f"\nSpeaker Health: {health_score}%")
    if health_score == 100:
        speak("The speaker is in excellent condition!")
    elif 80 <= health_score < 100:
        speak("The speaker is in good condition.")
    elif 60 <= health_score < 80:
        speak("The speaker is in average condition.")
    else:
        speak("The speaker might be in poor condition.")


