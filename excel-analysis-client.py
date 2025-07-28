import requests

# Define the API endpoint
url = "http://127.0.0.1:8000/process-file/"

# Define the file to upload and user messages
file_path = "testFile3_13kb.xlsx"  # Replace with the actual file path
user_messages = [
    "How many orders were placed in 2024?",
    "List all orders with a 'Total' value greater than $1000"
]

print("prcessing file...")
# Prepare the file and form data
with open(file_path, "rb") as file:
    files = {"file": file}
    data = [("user_messages", message) for message in user_messages]

    # Make the POST request
    response = requests.post(url, files=files, data=data)

# Print the response
if response.status_code == 200:
    print("Response from API:")
    print(response.json())
else:
    print(f"Failed to call API. Status code: {response.status_code}")
    print(response.text)