"""LLM provider abstraction for multiple backends."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        client = self._get_client()

        message = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

    def is_available(self) -> bool:
        return bool(self.api_key)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required: pip install openai")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        return bool(self.api_key)


class MockProvider(LLMProvider):
    """Mock provider for testing without API calls."""

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        # Return a mock response that acknowledges the context
        return (
            "Based on the Census Bureau data provided, I can see employment "
            "statistics for the requested geography. The data shows labor force "
            "participation rates and unemployment figures. [ACS-ACS5-2022-001]\n\n"
            "Sources:\n- U.S. Census Bureau, American Community Survey (2022)"
        )

    def is_available(self) -> bool:
        return True


def get_llm_provider(
    provider_name: str = "anthropic",
    api_key: str | None = None,
    model: str | None = None,
) -> LLMProvider:
    """Factory function to get an LLM provider.

    Args:
        provider_name: 'anthropic', 'openai', or 'mock'
        api_key: API key for the provider
        model: Model to use (provider-specific)

    Returns:
        Configured LLM provider
    """
    providers = {
        "anthropic": lambda: AnthropicProvider(
            api_key=api_key or "",
            model=model or "claude-sonnet-4-5-20250929",
        ),
        "openai": lambda: OpenAIProvider(
            api_key=api_key or "",
            model=model or "gpt-4o",
        ),
        "mock": lambda: MockProvider(),
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Use: {list(providers.keys())}")

    return providers[provider_name]()
