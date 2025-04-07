from dotenv import load_dotenv
import os
from composio_core import ComposioClient
from composio_langchain import ComposioToolkit

# Load environment variables
load_dotenv()

# Initialize Composio client
client = ComposioClient(api_key=os.getenv('COMPOSIO_API_KEY'))

# Create a toolkit with GitHub tools
toolkit = ComposioToolkit(client=client)
tools = toolkit.get_tools(apps=['github'])

# List repositories
for tool in tools:
    if tool.name == 'list_repositories':
        result = tool.run()
        print("\nYour GitHub Repositories:")
        for repo in result:
            print(f"- {repo['full_name']}")
