##  Excel Analysis API using Azure AI Agents Code Interpreter
This project provides a FastAPI-based backend to process Excel files and answer user-provided questions using Azure AI services. Additionally, it includes a Streamlit-based UI for uploading Excel files, submitting questions, and viewing results.

## Prerequisites
1. Python: Ensure Python 3.10 or higher is installed.
2. Set up an Azure AI Foundry project
3. Create a .env file in the project root with the following

```
PROJECT_CONNECTION_STRING : The project connection string, as found in the overview page of your Azure AI Foundry project.

MODEL_DEPLOYMENT_NAME : The deployment name of the AI model, as found under the "Name" column in the "Models + endpoints" tab in your Azure AI Foundry project.
```

4. Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

5. Install Dependencies
```
pip install -r requirements.txt
```

## Run the API
Run the following command to start the server:
```
uvicorn agents-code-interpreter-api:app --reload
```
The API will be available at: `http://127.0.0.1:8000/process-file/`

## Test the API using Curl command

```
curl -X POST "http://127.0.0.1:8000/process-file/" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@testFile3_13kb.xlsx" -F "user_messages=How many orders were placed in 2024?" -F "user_messages=List all orders with a 'Total' value greater than $1000"
```

## Test the API With a Client

Run the client: `python excel-analysis-client.py`

## Running the UI

Run the following command to start the UI:
```
streamlit run excel-analysis-ui.py
```

The UI will be available at: `http://localhost:8501`

## Cleanup

To stop the server or UI, press Ctrl+C in the terminal running the FastAPI server or Streamlit app.

## Reference
https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/code-interpreter?tabs=python&pivots=code-example

https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agents_code_interpreter.py

## Disclaimer
This Prototype/Proof of Concept (POC) sample template code can be utilized by customer and adapted according to their specific use cases and testing requirements. Microsoft or the author does not hold responsibility for the maintenance of customer code, production issues, or security vulnerabilities.

