"""Small command-line project for testing an OpenAI API key."""

import os
import sys
import argparse

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    OpenAIError,
)


def create_client() -> OpenAI:
    """Load environment variables and create an authenticated OpenAI client."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key."
        )

    return OpenAI(api_key=api_key)


def test_api(prompt: str, model: str) -> str:
    """Send one small Responses API request and return the generated text."""
    client = create_client()
    response = client.responses.create(
        model=model,
        input=prompt,
    )
    return (response.output_text or "").strip()


def main() -> int:
    """Parse command-line options, call the API, and report useful errors."""
    parser = argparse.ArgumentParser(
        description="Send a test request to the OpenAI API."
    )
    parser.add_argument(
        "--prompt",
        default="Reply with exactly: OpenAI API connection successful!",
        help="Text to send to the model.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model name. Defaults to OPENAI_MODEL in .env, or gpt-5.5.",
    )
    args = parser.parse_args()

    load_dotenv()
    model = args.model or os.getenv("OPENAI_MODEL", "gpt-5.5").strip()

    print(f"Testing OpenAI API with model: {model}")
    print("Sending request...")

    try:
        result = test_api(args.prompt, model)
        if not result:
            print("The API request completed, but the response contained no text.")
            return 2

        print("\nAPI TEST SUCCEEDED")
        print("-" * 60)
        print(result)
        print("-" * 60)
        return 0

    except RuntimeError as exc:
        print(f"\nConfiguration error: {exc}", file=sys.stderr)
        return 2
    except AuthenticationError:
        print(
            "\nAuthentication failed. Check that OPENAI_API_KEY is correct, "
            "active, and copied completely.",
            file=sys.stderr,
        )
        return 3
    except PermissionDeniedError:
        print(
            "\nPermission denied. Check the API key's project permissions "
            "and whether the project can use this model.",
            file=sys.stderr,
        )
        return 4
    except NotFoundError:
        print(
            "\nModel or endpoint not found. Check OPENAI_MODEL and choose a "
            "model available to your API project.",
            file=sys.stderr,
        )
        return 5
    except RateLimitError:
        print(
            "\nRate limit or quota error. Check project billing, available "
            "credits, and rate limits in the OpenAI Platform.",
            file=sys.stderr,
        )
        return 6
    except (APIConnectionError, APITimeoutError) as exc:
        print(
            f"\nCould not connect to the OpenAI API: {exc}\n"
            "Check your internet connection, firewall, proxy, and try again.",
            file=sys.stderr,
        )
        return 7
    except BadRequestError as exc:
        print(f"\nThe API rejected the request: {exc}", file=sys.stderr)
        return 8
    except OpenAIError as exc:
        print(f"\nOpenAI API error: {exc}", file=sys.stderr)
        return 9
    except Exception as exc:
        print(f"\nUnexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
