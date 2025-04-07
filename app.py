from dotenv import load_dotenv
from openai import OpenAI
from composio_openai import ComposioToolSet

load_dotenv()

# Initialize OpenAI client and Composio toolset
client = OpenAI()
toolset = ComposioToolSet()

# Define system message for better context
system_message = """You are a helpful assistant with access to GitHub actions through Composio.
You can perform various GitHub operations including repository creation and management.
When asked to perform actions, use the appropriate Composio tools to execute them."""

# Define the repository details
repo_name = "composio-demo"
repo_description = "A demo repository showcasing Composio's GitHub integration capabilities"

# Define the task
task = f"Please create a new GitHub repository named '{repo_name}' with the description: '{repo_description}'. Then initialize it with my local code."

# Create messages for the conversation
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": task},
]

# Get tools for repository creation
actions = toolset.find_actions_by_use_case(
    use_case="create github repository and push local code",
    advanced=True
)
tools = toolset.get_tools(actions=actions)

# Start the conversation loop
while True:
    # Get completion from OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        tools=tools,
        messages=messages,
    )

    # Handle any tool calls
    result = toolset.handle_tool_calls(response)

    # If no more tool calls, print the final message and break
    if response.choices[0].finish_reason != "tool_calls":
        print(response.choices[0].message.content)
        break

    # Add assistant's response to messages
    messages.append(
        {
            "role": "assistant",
            "content": "",
            "tool_calls": response.choices[0].message.tool_calls,
        }
    )

    # Add tool results to messages
    for tool_call in response.choices[0].message.tool_calls:
        messages.append(
            {
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call.id,
            }
        )
