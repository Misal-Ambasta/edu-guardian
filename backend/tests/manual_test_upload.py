import requests
import os

# Define the API endpoint
API_URL = "http://localhost:8000/api/students/upload-csv"

# Path to the test CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "test_data.csv")

def test_upload():
    """Test the CSV upload endpoint manually"""
    # Check if the file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: Test file not found at {CSV_FILE_PATH}")
        return
    
    # Open the file for reading
    with open(CSV_FILE_PATH, 'rb') as f:
        # Create the files dictionary for the request
        files = {
            'file': ('test_data.csv', f, 'text/csv')
        }
        
        # Send the POST request
        try:
            response = requests.post(API_URL, files=files)
            
            # Print the response status and content
            print(f"Status Code: {response.status_code}")
            print("Response:")
            print(response.json())
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Testing CSV upload endpoint...")
    test_upload()