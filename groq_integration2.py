import time
import signal
from groq import Groq
from google_sheets_util import write_to_sheet
import pandas as pd
import threading

# Global flag to handle script shutdown
shutdown_flag = False

# Groq API key
GROQ_API_KEY = "APIKEYHERE"  #USE THE API KEY CREATED IN GROQ WEBSITE
client = Groq(api_key=GROQ_API_KEY)

# Google Sheets configuration
SHEET_NAME = "Transcriptions and Responses"  

# Dataset path
DATASET_PATH = "mutual_funds_dataset.csv"

# Global customer name
customer_name = ""

# Load and preprocess the dataset
def load_and_preprocess_dataset(dataset_path):
    df = pd.read_csv(dataset_path)
    structured_text = ""
    for _, row in df.iterrows():
        structured_text += (
            f"Scheme Name: {row['scheme_name']}, Min SIP: {row['min_sip']}, "
            f"Expense Ratio: {row['expense_ratio']}, "
            f"Fund Size: {row['fund_size_cr']}, "
            f"Risk Level: {row['risk_level']} "
            f"Rating: {row['rating']}, Category: {row['category']}, "
            f" Return 1yr (%): {row['returns_1yr']}, "
            f"Return 3yr (%): {row['returns_3yr']}\n"
        )
    return structured_text

dataset_text = load_and_preprocess_dataset(DATASET_PATH)

# Load summaries for a specific customer
def load_customer_summaries(customer_name):
    try:
        with open("summaries.txt", "r") as f:
            summaries = f.readlines()
        customer_summaries = [
            line for line in summaries if line.startswith(f"{customer_name}:")
        ]
        return "\n".join(customer_summaries)
    except FileNotFoundError:
        print("summaries.txt not found. Proceeding without additional summaries.")
        return ""

# Process the text using the Groq API
def process_text_with_groq(text):
    try:
        customer_summaries = load_customer_summaries(customer_name)
        combined_context = (
            f"{dataset_text}\n\n"
            f"Additional summaries for {customer_name}:\n{customer_summaries}\n\n"
        )
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a mutual fund analyst specializing in analyzing investment data. "
                        "Use the following dataset and additional summaries to answer user queries and provide insights:\n\n"
                        f"{combined_context}\n\n"
                        "Always provide professional, concise, and data-driven responses. "
                        "Respond with sentiment and intent of the customer. "
                        "Also, provide a response that helps the salesperson convert the customer's intent into a positive one. "
                        "Negotiate with him well by advising better deals or improving the current advised deal."
                    )
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=512,
        )
        response = chat_completion.choices[0].message.content
        return response
    except Exception as e:
        return f"Error with Groq API: {e}"

# Save summary responses with customer name
def save_summary(responses):
    try:
        summary_line = f"{customer_name}: {responses}"
        with open("post_call_summary.txt", "w") as f:
            f.write(summary_line + "\n")
        print("Summary successfully saved in post_call_summary.txt.")
        
        with open("summaries.txt", "a") as f:
            f.write(summary_line + "\n")
        print("Summary successfully saved in summaries.txt.")
    except Exception as e:
        print(f"Error saving summary: {e}")

# Write to Google Sheets (Transcriptions and Responses sheet)
def write_to_transcriptions_sheet(sheet_name, conversation_data):
    try:
        write_to_sheet(sheet_name, conversation_data)
        print(f"Conversation written to Google Sheet '{sheet_name}'. Data: {conversation_data}")
    except Exception as e:
        print(f"Error writing to Google Sheet '{sheet_name}': {e}")
        
        
def generate_html_response(response):
    try:
        # Read the existing HTML file
        with open("assistant.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        # Locate the response container
        start_index = html_content.find('<div id="analysis" class="response-container">') + len('<div id="analysis" class="response-container">')
        if start_index == -1:
            raise ValueError("Response container not found in HTML content.")

        # Format the response as a list
        formatted_response = f"""
        <div class="response">
            <h2>Analysis Complete!</h2>
            <ul>
                {''.join(f'<li>{item.strip()}</li>' for item in response.split(','))}
            </ul>
        </div>
        """

        # Inject the response into the HTML
        end_index = html_content.find('</div>', start_index)
        updated_html = html_content[:start_index] + formatted_response + html_content[end_index:]

        # Write the updated HTML back to the file
        with open("assistant.html", "w", encoding="utf-8") as f:
            f.write(updated_html)

        print("Response successfully added to assistant.html.")

    except Exception as e:
        print(f"Error generating HTML response: {e}")


# Function to continuously monitor and process recognized text
def monitor_text():
    conversation_log = []

    while not shutdown_flag:
        try:
            with open("recognized_text.txt", "r") as f:
                text = f.read().strip()
        except FileNotFoundError:
            text = ""
        
        if text:
            response = process_text_with_groq(text)

            with open("recognized_text.txt", "w") as f:
                f.write(text)

            conversation_log.append({"user": text, "response": response})
            generate_html_response(response)
            write_to_transcriptions_sheet(SHEET_NAME, [text, response])

        time.sleep(3)

# Main function to initiate the monitoring process
def main():
    global shutdown_flag
    global customer_name

    print("Starting the Groq integration with text file handling and Google Sheets...")

    customer_name = input("Enter the customer's name: ").strip()

    text_monitor_thread = threading.Thread(target=monitor_text, daemon=True)
    text_monitor_thread.start()

    while True:
        user_input = input("Type 'exit' to stop the script and generate summary: ")
        if user_input.lower() == "exit":
            print("Exiting and generating the summary...")
            shutdown_flag = True
            break

    conversation_history = ""
    with open("recognized_text.txt", "r") as file:
        conversation_history = file.read().strip()

    if conversation_history:
        suggestions = process_text_with_groq(f"Conversation summary: {conversation_history}\nProvide suggestions and actions for future engagement with the customer.")
        save_summary(f"Summary and Suggestions: {suggestions}")
        write_to_transcriptions_sheet(SHEET_NAME, ["Summary and Suggestions", suggestions])

    print("Summary generated successfully.")

if __name__ == "__main__":
    main()
