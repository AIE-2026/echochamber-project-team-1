import os
from dotenv import load_dotenv
from openai import OpenAI

import core.config as config


PROVIDER_PRINCIPAL = getattr(config, "PROVIDER_PRINCIPAL", "gemini")
MODEL_PRINCIPAL = getattr(config, "MODEL_PRINCIPAL", "gemini-2.5-flash-lite")

PROVIDER_FALLBACK = getattr(config, "PROVIDER_FALLBACK", "gemini")
MODEL_FALLBACK = getattr(config, "MODEL_FALLBACK", "gemini-2.5-flash")

TEMPERATURE = getattr(config, "TEMPERATURE", 0.7)


BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openrouter": "https://openrouter.ai/api/v1",
}

ENV_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def make_client(provider: str) -> OpenAI:
    api_key_name = ENV_KEYS.get(provider)
    base_url = BASE_URLS.get(provider)

    if not api_key_name or not base_url:
        raise ValueError(f"Unknown provider: {provider}")

    api_key = os.getenv(api_key_name)

    if not api_key:
        raise ValueError(f"Missing API key: {api_key_name}")

    return OpenAI(api_key=api_key, base_url=base_url)


def ask_model(provider: str, model: str, prompt: str) -> str:
    client = make_client(provider)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant for political text analysis.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=TEMPERATURE,
    )

    return response.choices[0].message.content


def ask_with_fallback(prompt: str) -> str:
    try:
        print(f"Trying main model: {PROVIDER_PRINCIPAL} / {MODEL_PRINCIPAL}")
        return ask_model(PROVIDER_PRINCIPAL, MODEL_PRINCIPAL, prompt)

    except Exception as main_error:
        print(f"Main model failed: {main_error}")
        print(f"Trying fallback model: {PROVIDER_FALLBACK} / {MODEL_FALLBACK}")

        try:
            return ask_model(PROVIDER_FALLBACK, MODEL_FALLBACK, prompt)

        except Exception as fallback_error:
            return (
                "Both main and fallback models failed.\n"
                f"Main error: {main_error}\n"
                f"Fallback error: {fallback_error}"
            )


def main() -> None:
    load_dotenv()

    print("EchoChamber Studio — minimal terminal app")
    print(f"Main model: {PROVIDER_PRINCIPAL} / {MODEL_PRINCIPAL}")
    print(f"Fallback model: {PROVIDER_FALLBACK} / {MODEL_FALLBACK}")
    print(f"Temperature: {TEMPERATURE}")

    user_prompt = input("\nWrite a prompt: ")

    if not user_prompt.strip():
        print("No prompt provided.")
        return

    answer = ask_with_fallback(user_prompt)

    print("\n--- Model response ---")
    print(answer)


if __name__ == "__main__":
    main()