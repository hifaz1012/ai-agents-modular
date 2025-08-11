# AI Agents Utility - README

## Overview

The `ai-agents-utility.py` module is a comprehensive utility for working with Azure AI Agents and the Code Interpreter tool. This module provides a complete framework for creating AI agents that can analyze Excel and CSV files, enabling users to ask questions about their data and receive intelligent responses with code execution capabilities.

The utility demonstrates advanced Azure AI integration patterns including agent lifecycle management, file processing, conversation threading, and response handling with image generation support.

## Key Functionalities and Usage

### Core Features

- **Agent Management**: Create, retrieve, and manage Azure AI agents with code interpreter capabilities
- **Thread Management**: Handle conversation threads for maintaining context across multiple interactions
- **File Processing**: Upload and process Excel (.xlsx) and CSV files for analysis
- **Interactive Messaging**: Send messages with file attachments and receive detailed responses
- **Code Execution**: Leverage Azure's code interpreter for data analysis and visualization
- **Image Generation**: Automatically save generated charts and graphs from agent responses
- **Session Management**: Support for multiple chat sessions with proper cleanup

### Main Functions

#### Agent Operations
- `create_code_interpreter_agent()`: Creates or retrieves an existing AI agent with code interpreter tool
- `delete_agent(agent_id)`: Removes an agent when no longer needed

#### Thread Operations  
- `create_thread()`: Establishes a new conversation thread
- `delete_thread(thread_id)`: Cleans up conversation threads

#### File Operations
- `upload_file(file_path)`: Uploads files to the agent for analysis
- `delete_file(file_id)`: Removes uploaded files to free up space

#### Communication
- `create_message_with_file_attachment(thread_id, user_message, file_id)`: Sends messages with optional file attachments
- `run_agent(thread_id, agent_id)`: Executes the agent and processes responses

## Installation and Integration Instructions

### Prerequisites

1. **Azure AI Foundry Project**: You need an active Azure AI Foundry project
2. **Python Environment**: Python 3.7+ recommended
3. **Azure Authentication**: Proper Azure credentials configured

### Installation Steps

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file or set the following environment variables:
   
   ```bash
   PROJECT_CONNECTION_STRING="<your_azure_ai_project_connection_string>"
   MODEL_DEPLOYMENT_NAME="<your_model_deployment_name>"
   CODE_INTEPRETER_AGENT_NAME="<your_agent_name>"
   ```

3. **Azure Authentication**:
   Ensure you're logged into Azure CLI:
   ```bash
   az login
   ```

### Integration Instructions

To integrate this utility into your own projects:

1. Import the necessary functions:
   ```python
   from ai_agents_utility import (
       create_code_interpreter_agent,
       create_thread, 
       upload_file,
       create_message_with_file_attachment,
       run_agent
   )
   ```

2. Follow the established pattern of creating agent → thread → upload files → send messages → run agent.

## Example Usage

### Basic Usage Pattern

```python
import os
from ai_agents_utility import *

# Step 1: Create or get existing agent
agent_id = create_code_interpreter_agent()

# Step 2: Create a conversation thread
thread_id = create_thread()

# Step 3: Upload your data file
file_id = upload_file("your_data_file.xlsx")

# Step 4: Send a question about your data
create_message_with_file_attachment(
    thread_id, 
    "How many records are in this dataset?", 
    file_id
)

# Step 5: Get the AI response
result = run_agent(thread_id, agent_id)
print(f"AI Response: {result['response']}")

# Step 6: Cleanup
delete_file(file_id)
delete_thread(thread_id)
```

### Multiple Questions Session

```python
# Reuse the same thread for follow-up questions
create_message_with_file_attachment(
    thread_id, 
    "Show me the top 10 records by revenue", 
    file_id
)
result = run_agent(thread_id, agent_id)

create_message_with_file_attachment(
    thread_id, 
    "Create a chart showing revenue trends", 
    file_id
)
result = run_agent(thread_id, agent_id)
```

### Sample Questions for Excel/CSV Analysis

- "How many rows and columns are in this dataset?"
- "What are the unique values in the 'Category' column?"
- "Calculate the average, min, and max values for the 'Revenue' column"
- "Show me records where Total > $1000"
- "Create a bar chart of sales by region"
- "Find any duplicate entries in this dataset"
- "What is the correlation between different numeric columns?"

## Dependencies and Requirements

### Required Packages

The utility depends on the following packages (from `requirements.txt`):

- **azure-ai-projects**: Core Azure AI Projects SDK
- **azure-identity**: Azure authentication and credential management  
- **python-dotenv**: Environment variable management
- **pandas**: Data manipulation and analysis (used by code interpreter)
- **tiktoken**: Token counting for AI models
- **openpyxl**: Excel file reading/writing support
- **openai**: OpenAI API integration
- **fastapi**: Web framework (for API versions)
- **uvicorn**: ASGI server
- **python-multipart**: File upload support
- **streamlit**: Web UI framework (for UI versions)
- **opentelemetry-sdk**: Telemetry and tracing (for trace version)
- **azure-core-tracing-opentelemetry**: Azure OpenTelemetry integration
- **opentelemetry-exporter-otlp-proto-grpc**: Telemetry export

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PROJECT_CONNECTION_STRING` | Azure AI Foundry project connection string | Yes |
| `MODEL_DEPLOYMENT_NAME` | AI model deployment name from Azure | Yes | 
| `CODE_INTEPRETER_AGENT_NAME` | Name for the code interpreter agent | Yes |

### File Format Support

- **Excel Files**: .xlsx format
- **CSV Files**: Standard comma-separated values
- **File Size**: Tested with files up to 2MB
- **Image Output**: Generated charts saved as .png files

## API Documentation

### Function Reference

#### `create_code_interpreter_agent() -> str`
Creates or retrieves an existing AI agent with code interpreter capabilities.

**Returns**: Agent ID string

**Behavior**: 
- Checks if agent with specified name already exists
- Creates new agent if none found
- Returns the agent ID for further operations

#### `create_thread() -> str`
Creates a new conversation thread for agent communication.

**Returns**: Thread ID string

#### `upload_file(file_path: str) -> str`
Uploads a file to the Azure AI agent system.

**Parameters**:
- `file_path`: Path to the file to upload

**Returns**: File ID string

#### `create_message_with_file_attachment(thread_id: str, user_message: str, file_id: str) -> str`
Creates a message in the thread with optional file attachment.

**Parameters**:
- `thread_id`: ID of the conversation thread
- `user_message`: The question or instruction text
- `file_id`: ID of uploaded file (can be empty string for text-only messages)

**Returns**: Message ID string

#### `run_agent(thread_id: str, agent_id: str) -> dict`
Executes the agent and returns the response with metadata.

**Parameters**:
- `thread_id`: ID of the conversation thread
- `agent_id`: ID of the agent to execute

**Returns**: Dictionary containing:
- `run_id`: Execution run ID
- `run_status`: 1 for success, 0 for failure
- `response`: Agent's text response (if successful)
- `error`: Error details (if failed)
- `prompt_tokens`: Number of prompt tokens used
- `completion_tokens`: Number of completion tokens used
- `total_tokens`: Total tokens consumed

#### Cleanup Functions

- `delete_file(file_id: str)`: Removes uploaded file
- `delete_thread(thread_id: str)`: Deletes conversation thread
- `delete_agent(agent_id: str)`: Removes agent (optional cleanup)

## Error Handling and Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**: If you encounter rate limiting, the function will return error details. Wait a few seconds and retry.

2. **Authentication Failures**: Ensure your Azure credentials are properly configured and you have necessary permissions.

3. **File Upload Issues**: Verify file format is supported (.xlsx, .csv) and file size is reasonable.

4. **Agent Creation Failures**: Check that your model deployment name is correct and accessible.

### Response Status Codes

- **run_status = 1**: Successful execution
- **run_status = 0**: Failed execution (check error field)

## Related Files

This repository includes several related utilities:

- `ai-agents-utility-stream.py`: Streaming version with real-time response handling
- `ai-agents-utility-trace.py`: Version with OpenTelemetry tracing for monitoring
- `agents-code-interpreter-*.py`: Various specialized implementations

## Author and Maintainer Information

**Repository**: hifaz1012/ai-agents-modular  
**Primary Module**: ai-agents-utility.py  
**Framework**: Azure AI Projects SDK  
**Purpose**: Educational and demonstration samples for Azure AI Agents

### Disclaimer

This Prototype/Proof of Concept (POC) sample template code can be utilized by customers and adapted according to their specific use cases and testing requirements. Microsoft or the author does not hold responsibility for the maintenance of customer code, production issues, or security vulnerabilities.

### Contributing

This is a sample/demonstration repository. For issues or improvements:

1. Review the existing code patterns
2. Test thoroughly with your Azure AI setup
3. Follow the established error handling patterns
4. Ensure proper cleanup of resources

### Support and Documentation

- [Azure AI Services Agents Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- [Code Interpreter Tool Guide](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/code-interpreter?tabs=python&pivots=overview)
- [Azure AI Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)