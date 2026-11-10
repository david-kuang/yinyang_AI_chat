# OpenAI API Key Test (Python)

A small Windows-friendly Python project that sends one test request to the OpenAI
Responses API. It does **not** require ChatGPT Plus or Pro; API usage and billing
are managed separately in the OpenAI Platform.

## 1. Create an API key

1. Open the [OpenAI Platform](https://platform.openai.com/).
2. Select or create an API project.
3. Open [API keys](https://platform.openai.com/api-keys) and create a secret key
   for that project.
4. Copy the key immediately and keep it private. Do not paste it into chat,
   source code, screenshots, or public repositories.

If your project has no API billing or credits configured, the request may fail
with a quota or billing error. ChatGPT subscription billing is separate from
API billing.

## 2. Set up on Windows

Open Command Prompt and move to the folder where you extracted this project.
For example:

```bat
cd C:\workplaceyhk\pythonrelated\openai_api_python_test
```

Create and activate a virtual environment:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
```

If `py -3.12` is not recognized, try:

```bat
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Configure your API key

Copy the example environment file:

```bat
copy .env.example .env
```

Open `.env` in Notepad and replace `your_api_key_here` with your actual key:

```text
OPENAI_API_KEY=your_actual_secret_key
OPENAI_MODEL=gpt-5.5
```

Save the file. Do not include quotation marks unless they are part of the value.
Do not share the `.env` file. It is excluded by `.gitignore`.

If your project cannot access `gpt-5.5`, set `OPENAI_MODEL` to a model that
your API project is allowed to use.

## 4. Run the test

```bat
python main.py
```

A successful request prints:

```text
API TEST SUCCEEDED
------------------------------------------------------------
OpenAI API connection successful!
------------------------------------------------------------
```

You can also send your own prompt:

```bat
python main.py --prompt "Explain what an OpenAI API project is in two sentences."
```

Or choose a model for one run:

```bat
python main.py --model gpt-5.5 --prompt "Say hello."
```

## 5. Common errors

- **Authentication failed / 401:** key is incorrect, incomplete, revoked, or from
  the wrong environment variable.
- **Permission denied / 403:** check project key permissions and model access.
- **Model not found / 404:** change `OPENAI_MODEL` to a model available to your
  project.
- **Rate limit or quota / 429:** check API billing, credits, usage limits, and
  rate limits in the OpenAI Platform. A ChatGPT subscription does not include
  API credits.
- **Connection error:** check internet access, VPN, proxy, firewall, and retry.

Useful pages:

- [API keys](https://platform.openai.com/api-keys)
- [Usage](https://platform.openai.com/usage)
- [Billing](https://platform.openai.com/settings/organization/billing/overview)
- [Python SDK reference](https://developers.openai.com/api/reference/python)
- [Developer quickstart](https://developers.openai.com/api/docs/quickstart)
