Install the dependency:
Shell

pip install requests

Run it:
Shell
python test_claude.py
Expected result for a valid key:
Plain Text
Status Code: 200
✅ API Key is valid!
Claude Response:
SUCCESS
For extra security, you can load the API key from an environment variable instead of hardcoding it:
Python
import os
API_KEY = os.getenv("ANTHROPIC_API_KEY")
Then set it before running:
Shell
export ANTHROPIC_API_KEY="your_key_here" # Linux/macOS
PowerShell
$env:ANTHROPIC_API_KEY="your_key_here" # PowerShell

==============================chatgpt=======================================
create a python script so it will test my Claude API Key works.
Below is a simple Python script to test whether your Claude API Key from Anthropic is valid and whether you can successfully communicate with Claude's AI model.
The script will:
Read your API key securely from an environment variable.
Connect to Anthropic's Claude API.
Send a simple prompt: Hello Claude! Please introduce yourself.
Display Claude's response if successful.
Display useful error messages if the API key is invalid, authentication fails, or the API service encounters a problem.
1. Install the Anthropic Python library
Open Windows Command Prompt (inside your Python virtual environment if you use one):

pip install anthropic

2. Create test_claude_api.py
Save the following code in your Python project directory.
"""
Claude API Key Tester
Purpose: Verify that your Anthropic Claude API key works.
Python: 3.10+
Install: pip install anthropic
"""
import os
import sys
import getpass
import anthropic

MODEL = "claude-opus-5-5"


def main():
    """Test the Claude API key and send a sample prompt."""

    print("=" * 55)
    print("       ANTHROPIC CLAUDE API KEY TEST")
    print("=" * 55)

    # Read API key from environment or request it securely.
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        api_key = getpass.getpass(
            "\nEnter your Claude API Key: "
        ).strip()

    if not api_key:
        print("\nERROR: API key cannot be empty.")
        return 1

    try:
        print("\nConnecting to Anthropic Claude API...")
        print(f"Model: {MODEL}")

        client = anthropic.Anthropic(
            api_key=api_key,
            timeout=30.0,
            max_retries=1
        )

        response = client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Hello Claude! Please introduce yourself "
                        "in 3 short sentences."
                    )
                }
            ]
        )


3. Run the Python script
In Windows Command Prompt:

cd C:\workplaceyhk\pythonrelated\pyartifacts

python test_claude_api.py
The script will ask for your API key. Paste it when prompted. The key will not be displayed on screen.

Alternatively, set an environment variable:

set ANTHROPIC_API_KEY=your_api_key_here
python test_claude_api.py
4. Expected successful output
SUCCESS! YOUR CLAUDE API KEY WORKS!

Example output

Connecting to Anthropic Claude API...
Model: claude-opus-5-5

========================================================
SUCCESS! YOUR CLAUDE API KEY WORKS!
========================================================

Claude's Response:
Hello! I'm Claude, an AI assistant created by Anthropic.
I'm here to help answer questions and solve problems.

-------------------------------------------------------
API INFORMATION
-------------------------------------------------------
Model: claude-opus-5-5
Input tokens: 17
Output tokens: 30

TEST COMPLETED SUCCESSFULLY.
5. Troubleshooting
Error

Meaning

HTTP 401

Invalid API key

HTTP 403

Permission or access problem

HTTP 429

Rate limit or insufficient quota

HTTP 404

Model unavailable or incorrect model name

Connection error

Network connectivity problem

HTTP 500/529

Anthropic server-side problem

Important: A successful API call confirms that your key authenticates and can make a request. It does not mean API usage is free; check your Anthropic Console billing and usage.

Official documentation: Anthropic Python SDK.

Once this works, I can help you build a Python test application that compares OpenAI GPT, Google Gemini, and Anthropic Claude using the same prompt and measures response time, token usage, and API errors.

