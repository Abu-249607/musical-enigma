"""Application settings and configuration."""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Census API
    census_api_key: str = Field(default="", description="Census Bureau API key")
    census_mcp_path: str | None = Field(
        default=None, description="Path to Census MCP server"
    )

    # Cache settings
    cache_dir: str = Field(default="data/cache", description="Cache directory")
    cache_enabled: bool = Field(default=True, description="Enable caching")

    # Vector store settings
    vector_db_dir: str = Field(
        default="data/vectordb", description="Vector database directory"
    )
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model"
    )

    # LLM settings
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    default_llm_provider: str = Field(
        default="anthropic", description="Default LLM provider"
    )
    default_model: str = Field(
        default="claude-sonnet-4-5-20250929", description="Default model"
    )

    # RAG settings
    max_context_tokens: int = Field(
        default=4000, description="Max tokens for RAG context"
    )
    retrieval_top_k: int = Field(
        default=5, description="Number of chunks to retrieve"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
