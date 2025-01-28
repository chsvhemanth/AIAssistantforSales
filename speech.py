import pyaudio
import wave
import speech_recognition as sr
import threading
import time

# Function to capture audio from the Virtual Audio Cable (VAC)
def capture_audio_from_vac(record_seconds=5, output_filename="vac_audio.wav"):
    chunk = 2048
    format = pyaudio.paInt16
    channels = 1
    rate = 16000

    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=format, channels=channels, rate=rate, input=True,
                        frames_per_buffer=chunk, input_device_index=1)
        frames = []
        for _ in range(0, int(rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    except Exception as e:
        print(f"Error while recording audio: {e}")

# Function for speech-to-text conversion
def speech_to_text(audio_filename="vac_audio.wav"):
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_filename) as source:
            audio_data = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio_data)
                print(text)
                # Write the text to a file
                with open("recognized_text.txt", "w") as f:
                    f.write(text)
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                pass
            except Exception as e:
                pass

    except Exception as e:
        pass

# Continuous audio processing
def continuous_audio_processing():
    try:
        while True:
            capture_audio_from_vac(record_seconds=5, output_filename="vac_audio.wav")
            threading.Thread(target=speech_to_text, args=("vac_audio.wav",)).start()
            time.sleep(1)  # Shorter delay to process audio faster

    except KeyboardInterrupt:
        pass

def main():
    continuous_audio_processing()

if __name__ == "__main__":
    main()
