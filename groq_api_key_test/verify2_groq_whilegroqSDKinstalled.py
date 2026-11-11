#!/usr/bin/env python3

import os
from groq import Groq

def verify_groq_key():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("❌ GROQ_API_KEY environment variable is not set.")
        return

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Reply with OK"}
            ],
            max_tokens=5
        )

        print("✅ API key is valid")
        print("Response:", response.choices[0].message.content)

    except Exception as e:
        print("❌ API key verification failed")
        print("Error:", e)

if __name__ == "__main__":
    verify_groq_key()