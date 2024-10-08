import speech_recognition as sr
from os import getcwd

save_file = f'{getcwd()}\\input.txt'

def listen():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as the source for input
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)  # Reduce noise adjustment time

        print("Start speaking... (Press Ctrl+C to stop)")

        try:
            while True:
                print("Listening...")

                # Capture audio in small chunks
                audio = recognizer.listen(source, phrase_time_limit=2.5)  # Adjust phrase time limit

                try:
                    # Convert speech to text using Google Web Speech API
                    text = recognizer.recognize_google(audio)
                    print(f"Detected Text: {text}")

                    # Open the file in write mode to overwrite the previous text
                    with open(save_file, 'w') as file:
                        file.write(text)  # Write the latest recognized text
                        file.flush()  # Ensure text is written to the file immediately

                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand the audio.")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

        except KeyboardInterrupt:
            print("Real-time speech recognition stopped.")
