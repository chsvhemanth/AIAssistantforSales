import threading
import speech  # Assuming speech.py is the module for speech handling
import groq_integration2  # Your Groq integration logic

# Function to run the speech module
def run_speech():
    print("Starting speech processing...")
    speech.main()  # this is where the speech functionality is defined

# Function to run the Groq integration module
def run_groq():
    print("Starting Groq integration...")
    groq_integration2.main()  # Running  groq_integration2.py

if __name__ == "__main__":
    # Creating threads for running speech and groq_integration2 concurrently
    speech_thread = threading.Thread(target=run_speech)
    groq_thread = threading.Thread(target=run_groq)

    # Starting the threads
    speech_thread.start()
    groq_thread.start()

    # Ensuring the main program waits for both threads to finish before exiting
    speech_thread.join()
    groq_thread.join()

    print("Both speech processing and Groq integration are running.")
