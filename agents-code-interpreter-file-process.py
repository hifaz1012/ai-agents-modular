"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the code interpreter tool to 
    analyze excel and csv files

USAGE:
    python agents-code-interpreter.py

    Before running the sample:

    pip install -r requirements.txt

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.ai.projects.models import FilePurpose
from azure.identity import DefaultAzureCredential
from pathlib import Path

from dotenv import load_dotenv
import time

load_dotenv()

# Create an Azure AI Client from a connection string, copied from your Azure AI Foundry project.
# It should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# To Use DefaultAzureCredential, login to Azure subscription via Azure CLI
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

# process_file function to upload a file, create an agent, create a thread, and execute runs
def process_file(file_id: str, user_messages: list):
    # Upload a file and add it to the client
    start_time = time.time()
    # file = project_client.agents.upload_file_and_poll(
    #     file_path=file_path, purpose=FilePurpose.AGENTS
    # )
    print(f"Uploaded file, file ID: {file_id}")
    end_time = time.time()
    print(f"Time taken for File Upload: {end_time - start_time} seconds")

    code_interpreter = CodeInterpreterTool(file_ids=[file_id])
    start_time = time.time()
    # create agent with code interpreter tool and tools_resources
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="data-analysis-agent",
        instructions="You are AI Assistant to analyze excel and csv files. "
        "Think and Validate your answer. If there are multiple rows, present them in a table format.",
        #"Explain how you arrived at the answer and also output the code.",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    end_time = time.time()
    print(f"Time taken for Agent Creation: {end_time - start_time} seconds")

    start_time = time.time()
    # create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    for user_message in user_messages:
        # create a message
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )
      
        # create and execute a run
        run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")
        
        print("\n **Question**: ", user_message)

        print(f"Created message, message ID: {message.id}")

        print("\n 🤖 Thought Process: \n")

        # print the messages from the agent

        all_messages = project_client.agents.list_messages(thread_id=thread.id, run_id=run.id)
        # print(f"Messages: {messages}")
        filtered_messages = [msg for msg in all_messages.data if msg.run_id == run.id]
        # print(f"Filtered Messages : {filtered_messages}")
        
        if filtered_messages:
            # Sort messages by 'created_at' timestamp in ascending order
            sorted_messages = sorted(filtered_messages, key=lambda x: x.created_at)

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
        
        # save the newly created file
        for image_content in all_messages.image_contents:
            print(f"Image File ID: {image_content.image_file.file_id}")
            file_name = f"{image_content.image_file.file_id}_image_file.png"
            project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
            print(f"Saved image file to: {Path.cwd() / file_name}")
    
    end_time = time.time()
    print(f"Time taken for Query: {end_time - start_time} seconds")
    # delete the original file from the agent to free up space (note: this does not delete your version of the file)
    #project_client.agents.delete_file(file_id)
    #print("Deleted file")

    # Delete the assistant when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")


# Run using test excel file
# process_file("testFile1_2mb.xlsx", ["Find the email address of the person named Joyce Brown", 
#                                     "What is the phone number of the person who works at Dach, Christiansen and Conn",
#                                     "List all people who live in NM (New Mexico)?"])


# process_file("testFile3_13kb.xlsx", ["How many orders were placed in 2024?", 
#                                     "List all orders with a 'Total' value greater than $1000"])

#process_file("Northwind_Standard_Benefits_Details.pdf", ["What is covered in insurance plan?"])

start_time = time.time()
process_file("assistant-HjipaJYNoYSgR8MRPS1zHV", ["Find the email address of the person named Joyce Brown"])
#process_file("testFile1_2mb.xlsx", ["Find the email address of the person named Joyce Brown"])
end_time = time.time()
print(f"Overall Time: {end_time - start_time} seconds")
