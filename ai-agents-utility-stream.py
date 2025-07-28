"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the code interpreter tool to 
    analyze excel and csv files

USAGE:
    python ai-agents-utility.py

    Before running the sample:

    pip install -r requirements.txt

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) CODE_INTEPRETER_AGENT_NAME - The name of the code interpreter agent to be created.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, MessageAttachment
from azure.ai.projects.models import FilePurpose
from azure.identity import DefaultAzureCredential, EnvironmentCredential
from pathlib import Path

from dotenv import load_dotenv
import time

import json
from typing import Generator, Optional


from azure.ai.projects.models import (
    MessageDeltaChunk,
    MessageDeltaTextContent,
)
from azure.ai.projects.models import AgentStreamEvent, BaseAgentEventHandler

from typing import Any, Optional

load_dotenv()

# Create an Azure AI Client from a connection string, copied from your Azure AI Foundry project.
# It should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# To Use DefaultAzureCredential, login to Azure subscription via Azure CLI# Our goal is to parse the event data in a string and return the chunk in text for each iteration.
# Because we want the iteration to be a string, we define str as the generic type for BaseAsyncAgentEventHandler
# and override the _process_event method to return a string.
# The get_stream_chunks method is defined to return the chunks as strings because the iteration is a string.
class MyEventHandler(BaseAgentEventHandler[Optional[str]]):

    def _process_event(self, event_data_str: str) -> Optional[str]:  # type: ignore[return]
        event_lines = event_data_str.strip().split("\n")
        event_type: Optional[str] = None
        event_data = ""
        for line in event_lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()

        if not event_type:
            raise ValueError("Event type not specified in the event data.")

        if event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA.value:

            event_obj: MessageDeltaChunk = MessageDeltaChunk(**json.loads(event_data))

            for content_part in event_obj.delta.content:
                if isinstance(content_part, MessageDeltaTextContent):
                    if content_part.text is not None:
                        return content_part.text.value
        return None

    def get_stream_chunks(self) -> Generator[str, None, None]:
        for chunk in self:
            if chunk:
                yield chunk

project_client = AIProjectClient.from_connection_string(
    credential=EnvironmentCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)
#project_client.telemetry.get_connection_string()
# create agent with code interpreter tool and tools_resources if it does not exis
def create_code_interpreter_agent():
    # Create an agent with the code interpreter tool
    CODE_INTEPRETER_AGENT_NAME = os.environ["CODE_INTEPRETER_AGENT_NAME"]
    
    agent = None
    all_agents_list = project_client.agents.list_agents().data
    for a in all_agents_list:
        if a.name == CODE_INTEPRETER_AGENT_NAME:
            agent = a
            print(f"Agent {CODE_INTEPRETER_AGENT_NAME} already exists with Id {a.id}.")
            break

    if agent is None:
        code_interpreter = CodeInterpreterTool()
        agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name=CODE_INTEPRETER_AGENT_NAME,
            instructions="You are AI Assistant to analyze excel and csv files. "
            "If there are multiple rows, present them in a table format.",
            tools=CodeInterpreterTool().definitions
        )
        print(f"Created agent, agent ID: {agent.id}")
    return agent.id


# create a thread for the agent communication
def create_thread():
    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")
    return thread.id

# Upload a file to the agent
def upload_file(file_path: str):
    # Upload a file and add it to the client
    file = project_client.agents.upload_file_and_poll(
        file_path=file_path, purpose=FilePurpose.AGENTS
    )
    print(f"Uploaded file, file ID: {file.id}")
    return file.id

# create a message with file attachment
def create_message_with_file_attachment(thread_id: str, user_message: str, file_id: str):
    print("\n **Question**: ", user_message)
    if file_id:
        # Create an attachment
        attachment = MessageAttachment(file_id=file_id, tools=CodeInterpreterTool().definitions)
        # Create a message with code interpreter file
        message = project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=user_message,
            attachments=[attachment]
        )
        print(f"Created message with file, message ID: {message.id}")
    else:
        # Create a message without file attachment
        message = project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=user_message,
        )
        print(f"Created message, message ID: {message.id}")
    
    return message.id    

# run the agent with the thread ID and agent ID
# This is used to execute the agent and get the response
# run status is 0 for failed and 1 for success
# if you get "Rate limit is exceeded.", attempt a retry after a few seconds
def run_agent(thread_id: str, agent_id: str):   
    # Create and execute a run
    run = project_client.agents.create_and_process_run(thread_id=thread_id, agent_id=agent_id)
    print(f"Run finished with status: {run.status}")

    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = project_client.agents.get_run(thread_id=thread_id, run_id=run.id)

        print(f"Run status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")
        return {"run_id":run.id, "run_status":0, "error": run.last_error, "prompt_tokens":run.usage.prompt_tokens, 
            "completion_tokens": run.usage.completion_tokens, "total_tokens": run.usage.total_tokens}
    
    print("\n 🤖 Thought Process: \n")

    # print the messages from the agent

    all_messages = project_client.agents.list_messages(thread_id=thread_id, run_id=run.id)
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
    
   
    
    return {"run_id":run.id, "run_status":1, "response": last_msg.text.value, 
            "prompt_tokens":run.usage.prompt_tokens, 
            "completion_tokens": run.usage.completion_tokens, "total_tokens": run.usage.total_tokens}

def run_agent_stream(thread_id: str, agent_id: str): 
     with project_client.agents.create_stream(
        thread_id=thread_id, agent_id=agent_id, event_handler=MyEventHandler()
    ) as stream:
        for chunk in stream.get_stream_chunks():
            print(chunk)


# delete the file from the agent
def delete_file(file_id: str):
    # delete the original file from the agent to free up space (note: this does not delete your version of the file)
    project_client.agents.delete_file(file_id)
    print("Deleted file")

# delete the thread from the agent
def delete_thread(thread_id: str):
    # Delete the thread when done
    project_client.agents.delete_thread(thread_id)
    print("Deleted thread")

# delete the agent
def delete_agent(agent_id: str):
    # Delete the assistant when done
    project_client.agents.delete_agent(agent_id)
    print("Deleted agent")

# Simulate Chat and Run using test excel files ##

######## Start of Chat Session 1 ########
print("######## Start of Chat Session 1 ########")
agent_id = create_code_interpreter_agent()
thread_id = create_thread()

# Upload file 1
file_id1 = upload_file("testFile3_13kb.xlsx")

# First message to the agent
create_message_with_file_attachment(thread_id, "How many orders were placed in 2024?", file_id1)
run_agent_stream(thread_id, agent_id)


# # Second message to the agent
# create_message_with_file_attachment(thread_id, "List all orders with a 'Total' value greater than $1000?", file_id1)
# result = run_agent(thread_id, agent_id)
# print(f"Result: {result}")

# # Upload file 2
# file_id2 = upload_file("testFile1_2mb.xlsx")
# # Third message to the agent
# create_message_with_file_attachment(thread_id, "Find the email address of the person named Joyce Brown?", file_id2)
# result = run_agent(thread_id, agent_id)
# print(f"Result: {result}")

# Clean up: delete the uploaded files and thread
delete_file(file_id1)  
delete_thread(thread_id)

print("######## End of Chat Session 1 ########")
####### End of Chat Session 1 ########

# ####### Start of Chat Session 2 - new thread ########
# print("######## Start of Chat Session 2 ########")

# # Reuse the agent from previous session
# agent_id = create_code_interpreter_agent()

# # Create a new thread for the agent communication
# thread_id = create_thread()

# # reuse exisiting file from previous session file_id2
# # First message to the agent
# create_message_with_file_attachment(thread_id, "What is the phone number of the person who works at Dach, Christiansen and Conn?", file_id2)
# result = run_agent(thread_id, agent_id)
# print(f"Result: {result}")

# # Upload file new
# file_id3 = upload_file("testFile2_1MB.xlsx")

# # Second message to the agent
# create_message_with_file_attachment(thread_id, "What is revenue for east region?", file_id3)
# result = run_agent(thread_id, agent_id)
# print(f"Result: {result}")

# # Clean up: delete the uploaded files and thread
# delete_file(file_id2) 
# delete_file(file_id3)  
# delete_thread(thread_id)
# print("######## End of Chat Session 2 ########")
# ######## End of Chat Session 2 ########

# Optional: delete the agent if you want to clean up
delete_agent(agent_id)



