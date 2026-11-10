1. Install the dependency
bash
pip install openai
2. Set your API key as an environment variable
It's best practice not to hardcode your key. Set it in your terminal first:
bash
# macOS / Linux
export DEEPSEEK_API_KEY="sk-your-actual-key-here"
# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="sk-your-actual-key-here"
3. Create the test script (test_deepseek.py)
Save this file. It initializes the client, sends a simple "Hello" message, and prints the response to confirm your key works.

python
import os
from openai import OpenAI

# Initialize the client with DeepSeek's base URL
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def test_api_key():
    print("Testing DeepSeek API key...")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # Current standard model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Reply with 'API key is working' if you receive this."}
            ],
            stream=False,
            max_tokens=50
        )
        
        # Extract and print the response
        reply = response.choices[0].message.content
        print("\n✅ Success! Server responded:")
        print(f"   {reply}")
        print(f"\n   Model used: {response.model}")
        print(f"   Tokens used: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"\n❌ Failed to connect. Error: {e}")
        print("\nChecklist:")
        print("1. Is your DEEPSEEK_API_KEY environment variable set correctly?")
        print("2. Do you have internet access to api.deepseek.com?")
        print("3. Is your API key active and does it have sufficient balance?")

if __name__ == "__main__":
    test_api_key()
4. Run the script
bash
python test_deepseek.py