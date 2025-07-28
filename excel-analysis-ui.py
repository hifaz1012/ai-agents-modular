import streamlit as st
import requests

# Define the API endpoint
API_URL = "http://127.0.0.1:8000/process-file/"

# Title of the app
st.title("Excel Analysis Tool using Code Interpreter")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

# Text area for user questions
user_questions = st.text_area(
    "Enter your questions (one per line):",
    placeholder="Example:\nHow many orders were placed in 2024?\nList all orders with a 'Total' value greater than $1000",
)

# Submit button
if st.button("Submit"):
    if uploaded_file is None:
        st.error("Please upload an Excel file.")
    elif not user_questions.strip():
        st.error("Please enter at least one question.")
    else:
        # Prepare the file and questions
        files = {"file": uploaded_file.getvalue()}
        questions = user_questions.strip().split("\n")
        data = [("user_messages", question) for question in questions]

        # Make the POST request
        with st.spinner("Processing..."):
            response = requests.post(API_URL, files={"file": uploaded_file}, data=data)

        # Display the results
        if response.status_code == 200:
            st.success("Processing complete!")
            results = response.json().get("results", [])
            time_taken = response.json().get("time_taken", [])
            for result in results:
                st.subheader(f"Question: {result['question']}")
                st.write(f"Response: {result['response']}")
            st.write(f"Time Taken: {time_taken} seconds")
        else:
            st.error(f"Failed to process the file. Status code: {response.status_code}")
            st.write(response.text)