import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


def create_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is required when LLM_PROVIDER=gemini"
            )

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            google_api_key=api_key,
            temperature=0,
        )

    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        temperature=0,
        keep_alive="30m",
    )