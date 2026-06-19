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
        print("ENTERED FALLBACK")
        last_exception = None

        for provider in self.providers:
            print(f"Trying {provider}")
            try:
                print(f"Trying {provider.__class__.__name__}")
                return provider.invoke(prompt)

            except Exception as e:
                print("INSIDE EXCEPT")
                print("Exception type:", type(e))
                print("Exception name:", type(e)._name_)
                print("Exception message:", e)

                if self._should_fallback(e):
                    print("Falling back...")
                    last_exception = e
                    continue

                raise

        raise last_exception

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

        return isinstance(e, retryable)
llm = FallbackLLM([
    openai_llm,
    gemini_llm,
    ollama_llm
])