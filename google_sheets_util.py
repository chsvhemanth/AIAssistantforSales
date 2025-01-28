import gspread
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow


def authenticate_google_sheets():
    try:
        
        client_secrets_file = "credentials.json"
        storage_file = "storage.json" 

       
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

       
        flow = flow_from_clientsecrets(client_secrets_file, scope)
        storage = Storage(storage_file)

        # Checking if credentials already exist
        credentials = storage.get()
        if not credentials or credentials.invalid:
            credentials = run_flow(flow, storage)

        # Authorize the gspread client
        client = gspread.authorize(credentials)
        return client

    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

# Function to write data to Google Sheets
def write_to_sheet(sheet_name, data):
    try:
        # Authenticate and get the client
        client = authenticate_google_sheets()
        if not client:
            raise Exception("Failed to authenticate with Google Sheets.")

        # Open the sheet and append data
        sheet = client.open(sheet_name).sheet1
        sheet.append_row(data)
        print("Transcription and response written to Google Sheet.")
    except Exception as e:
        print(f"Error writing to Google Sheet: {e}")

# Example usage
if __name__ == "__main__":
    # Example data to write (Transcription and response)
    sheet_name = "Your Google Sheet Name"
    data = ["Sample Transcription", "Sample Response"]
    write_to_sheet(sheet_name, data)
