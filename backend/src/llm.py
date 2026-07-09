from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from openai import (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

from google.api_core.exceptions import (
    ResourceExhausted,
    ServiceUnavailable,
    DeadlineExceeded,
)
load_dotenv()

# OpenAI
openai_llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

# Gemini
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# Ollama
ollama_llm = ChatOllama(
    model="qwen2.5vl:7b",
    temperature=0
)
class FallbackLLM:

    def __init__(self, providers):
        self.providers = providers

    def invoke(self, prompt):
        last_exception = None

        for provider in self.providers:
            try:
                print(f"Trying {provider.__class__.__name__}")
                return provider.invoke(prompt)

            except Exception as e:
                print("INSIDE EXCEPT")
                print("Exception type:", type(e))
                print("Exception name:", type(e).__name__)
                print("Exception message:", e)

                if self._should_fallback(e):
                    print("Falling back...")
                    last_exception = e
                    continue

                raise

        if last_exception is not None:
            raise last_exception

        raise RuntimeError("No LLM providers available")

    @staticmethod
    def _should_fallback(e):

        retryable = (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            APIStatusError,
            ResourceExhausted,
            ServiceUnavailable,
            DeadlineExceeded,
        )

        if isinstance(e, retryable):
            return True

        status_code = getattr(e, "status_code", None)
        if status_code == 429:
            return True

        response = getattr(e, "response", None)
        if getattr(response, "status_code", None) == 429:
            return True

        message = str(e).lower()
        return (
            "insufficient_quota" in message
            or "rate limit" in message
            or "quota" in message
        )
llm = FallbackLLM([
    openai_llm,
    gemini_llm,
    ollama_llm
])