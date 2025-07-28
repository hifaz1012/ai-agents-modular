from fastapi import FastAPI, UploadFile, Form
from typing import List
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, FilePurpose
from azure.identity import DefaultAzureCredential
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Azure AI Client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

# Initialize FastAPI app
app = FastAPI()

@app.post("/process-file/")
async def process_file(file: UploadFile, user_messages: List[str] = Form(...)):

    # Capture the start time
    start_time = time.time()

    # Create a temporary directory if it doesn't exist
    os.makedirs("./temp", exist_ok=True)
    # Save the uploaded file locally
    file_path = f"./temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Upload the file to Azure AI
    uploaded_file = project_client.agents.upload_file_and_poll(
        file_path=file_path, purpose=FilePurpose.AGENTS
    )
    print(f"Uploaded file, file ID: {uploaded_file.id}")

    code_interpreter = CodeInterpreterTool(file_ids=[uploaded_file.id])
    

    # Create agent with code interpreter tool
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="data-analysis-agent",
        instructions="You are AI Assistant to analyze excel and csv files. "
        "Think and Validate your answer. If there are multiple rows, present them in a table format.",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    results = []

    for user_message in user_messages:
        # Create a message
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )

        # Create and execute a run
        run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
             # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")
        
        print("\n **Question**: ", user_message)

        print(f"Created message, message ID: {message.id}")

        print("\n 🤖 Thought Process: \n")

        # Get messages from the agent
        all_messages = project_client.agents.list_messages(thread_id=thread.id, run_id=run.id)
        filtered_messages = [msg for msg in all_messages.data if msg.run_id == run.id]

        if filtered_messages:
            sorted_messages = sorted(filtered_messages, key=lambda x: x.created_at)
            response_text = []
            for msg in sorted_messages:
                if msg.content and isinstance(msg.content, list):
                    for content_item in msg.content:
                        if content_item["type"] == "text":
                            print(f" {content_item['text']['value']}")

        # get the most recent message from the assistant
        last_msg = all_messages.get_last_text_message_by_role("assistant")
        if last_msg:
            print("\n")
            print(f"**Response from Agent**: {last_msg.text.value}")             
            response_text.append(last_msg.text.value)
            results.append({"question": user_message, "response": " ".join(response_text)})

    end_time = time.time()
    print(f"Time taken to process: {end_time - start_time} seconds")

    # Clean up: delete the uploaded file and agent
    project_client.agents.delete_file(uploaded_file.id)
    project_client.agents.delete_agent(agent.id)
    print("Deleted file and agent")

    # Return results
    return {"results": results, "time_taken": end_time - start_time}