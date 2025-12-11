"""Conversational RAG pipeline with multi-turn support."""

from typing import Any, Optional, List, Dict
from datetime import datetime
import uuid

from ..models.citation import Citation, CitedDataPoint
from ..census_client import CensusMCPClient
from .vector_store import CensusVectorStore
from .search import HybridSearcher
from .conversation import (
    ConversationMemory,
    ConversationContext,
    MessageRole,
    QueryRewriter,
)


class ConversationalRAGPipeline:
    """Enhanced RAG pipeline with conversation memory and multi-turn support.

    Features:
    - Conversation history tracking
    - Context-aware query rewriting
    - Citation accumulation across turns
    - Multi-turn employment insights
    """

    def __init__(
        self,
        census_client: Optional[CensusMCPClient] = None,
        vector_store: Optional[CensusVectorStore] = None,
        api_key: Optional[str] = None,
        enable_memory: bool = True,
    ):
        """Initialize the conversational RAG pipeline.

        Args:
            census_client: Pre-configured Census MCP client
            vector_store: Pre-configured vector store
            api_key: Census API key (used if client not provided)
            enable_memory: Whether to enable conversation memory
        """
        self.client = census_client or CensusMCPClient(api_key=api_key)
        self.vector_store = vector_store or CensusVectorStore()
        self.searcher = HybridSearcher(self.vector_store)
        self.query_rewriter = QueryRewriter()

        self.enable_memory = enable_memory
        self.memory = ConversationMemory() if enable_memory else None

        # Import chunker for data ingestion
        from ..preprocessing.chunker import DataChunker
        self.chunker = DataChunker()

    def ingest_geography(
        self,
        geography_name: str,
        years: List[int] | None = None,
        include_industry: bool = True,
    ) -> int:
        """Ingest employment data for a geography into the vector store.

        Args:
            geography_name: State or county name
            years: Years to ingest (default: [2024])
            include_industry: Whether to include industry breakdown

        Returns:
            Number of chunks ingested
        """
        years = years or [2024]
        total_chunks = 0

        for year in years:
            # Fetch employment data
            try:
                record, citation = self.client.get_employment_data(
                    geography_name, year=year
                )

                # Create chunks
                chunks = self.chunker.chunk_employment_record(record, citation)
                total_chunks += self.vector_store.add_chunks(chunks)

            except Exception as e:
                print(f"Warning: Could not ingest {geography_name} {year}: {e}")

            # Fetch industry data if requested
            if include_industry:
                try:
                    industry_data, industry_citation = self.client.get_industry_employment(
                        geography_name, year=year
                    )

                    industry_chunks = self.chunker.chunk_industry_data(
                        industry_data, geography_name, year, industry_citation
                    )
                    total_chunks += self.vector_store.add_chunks(industry_chunks)

                except Exception as e:
                    print(f"Warning: Could not ingest industry data for {geography_name}: {e}")

        return total_chunks

    def start_conversation(self, conversation_id: Optional[str] = None) -> str:
        """Start a new conversation.

        Args:
            conversation_id: Optional custom conversation ID

        Returns:
            Conversation ID
        """
        if not self.enable_memory:
            raise RuntimeError("Conversation memory is not enabled")

        conv_id = conversation_id or str(uuid.uuid4())
        self.memory.create_conversation(conv_id)
        return conv_id

    def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        n_results: int = 5,
        include_context: bool = True,
    ) -> Dict[str, Any]:
        """Have a conversational interaction with the RAG system.

        Args:
            query: User's question
            conversation_id: Conversation ID (creates new if None)
            n_results: Number of relevant chunks to retrieve
            include_context: Whether to include conversation context

        Returns:
            Response dictionary with answer, context, citations
        """
        # Get or create conversation context
        if self.enable_memory:
            if not conversation_id:
                conversation_id = self.start_conversation()

            conversation = self.memory.get_conversation(conversation_id)
        else:
            conversation = None

        # Add user message to conversation
        if conversation:
            conversation.add_message(MessageRole.USER, query)

        # Rewrite query with conversation context if needed
        if conversation and include_context:
            contextualized_query = self.query_rewriter.rewrite_with_context(
                query, conversation, n_context_messages=3
            )
        else:
            contextualized_query = query

        # Search for relevant information
        search_results = self.searcher.search(
            contextualized_query, n_results=n_results
        )

        # Extract citations
        citations = []
        seen_citation_ids = set()
        for result in search_results:
            citation_id = result["metadata"].get("citation_id")
            if citation_id and citation_id not in seen_citation_ids:
                citations.append({
                    "citation_id": citation_id,
                    "dataset": result["metadata"].get("dataset", "acs/acs5"),
                    "year": result["metadata"].get("year"),
                    "geography": result["metadata"].get("geography_name"),
                })
                seen_citation_ids.add(citation_id)

        # Build context for response
        context_parts = []
        for result in search_results:
            # Handle different possible key names from search results
            text = result.get("text") or result.get("document") or result.get("content", "")
            if text:
                context_parts.append(text)

        context = "\n\n".join(context_parts)

        # Extract geography if mentioned
        geography = None
        if conversation:
            geography = self.query_rewriter.extract_geography_from_context(
                conversation
            )

        response = {
            "conversation_id": conversation_id,
            "query": query,
            "contextualized_query": contextualized_query if include_context else None,
            "context": context,
            "citations": citations,
            "geography_context": geography,
            "search_results": search_results,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return response

    def get_conversation_history(
        self,
        conversation_id: str,
        n_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history.

        Args:
            conversation_id: Conversation ID
            n_messages: Number of recent messages (None = all)

        Returns:
            List of message dictionaries
        """
        if not self.enable_memory:
            return []

        conversation = self.memory.get_conversation(
            conversation_id, create_if_missing=False
        )

        if not conversation:
            return []

        messages = conversation.messages
        if n_messages:
            messages = messages[-n_messages:]

        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "citations": msg.citations,
                "metadata": msg.metadata,
            }
            for msg in messages
        ]

    def add_assistant_response(
        self,
        conversation_id: str,
        response: str,
        citations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add an assistant response to the conversation.

        Args:
            conversation_id: Conversation ID
            response: Assistant's response text
            citations: Citation IDs used in response
            metadata: Additional metadata
        """
        if not self.enable_memory:
            return

        conversation = self.memory.get_conversation(conversation_id)
        if conversation:
            conversation.add_message(
                MessageRole.ASSISTANT,
                response,
                citations=citations,
                metadata=metadata,
            )

    def clear_conversation(self, conversation_id: str):
        """Clear a conversation history.

        Args:
            conversation_id: Conversation ID to clear
        """
        if self.enable_memory and self.memory:
            self.memory.delete_conversation(conversation_id)

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all active conversations.

        Returns:
            List of conversation summaries
        """
        if not self.enable_memory or not self.memory:
            return []

        return self.memory.list_conversations()

    def compare_geographies_conversational(
        self,
        geographies: List[str],
        metric: str = "unemployment",
        year: int = 2024,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compare geographies with conversation context.

        Args:
            geographies: List of geography names
            metric: Metric to compare
            year: Data year
            conversation_id: Optional conversation ID

        Returns:
            Comparison results with citations
        """
        results = {}

        for geo in geographies:
            try:
                record, citation = self.client.get_employment_data(
                    geo, year=year, dataset="acs/acs1"
                )

                results[geo] = {
                    "unemployment_rate": record.unemployment_rate,
                    "labor_force_participation": record.labor_force_participation_rate,
                    "employment_population_ratio": record.employment_population_ratio,
                    "labor_force": record.labor_force,
                    "employed": record.employed,
                    "unemployed": record.unemployed,
                    "citation": citation.to_reference_string(),
                    "citation_id": citation.citation_id,
                }
            except Exception as e:
                results[geo] = {"error": str(e)}

        # Add to conversation if ID provided
        if conversation_id and self.enable_memory:
            conversation = self.memory.get_conversation(conversation_id)
            if conversation:
                summary = f"Compared {metric} across {', '.join(geographies)} for {year}"
                conversation.add_message(
                    MessageRole.ASSISTANT,
                    summary,
                    metadata={"comparison": results}
                )

        return {
            "comparison_year": year,
            "metric_focus": metric,
            "geographies": results,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_employment_insights(
        self,
        geography: str,
        year: int = 2024,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get employment insights for a geography.

        Args:
            geography: Geography name
            year: Data year
            conversation_id: Optional conversation ID

        Returns:
            Employment insights with citations
        """
        try:
            record, citation = self.client.get_employment_data(
                geography, year=year, dataset="acs/acs1"
            )

            insights = {
                "geography": geography,
                "year": year,
                "unemployment_rate": record.unemployment_rate,
                "labor_force_participation": record.labor_force_participation_rate,
                "employment_population_ratio": record.employment_population_ratio,
                "total_population_16_plus": record.total_population_16_plus,
                "labor_force": record.labor_force,
                "employed": record.employed,
                "unemployed": record.unemployed,
                "not_in_labor_force": record.not_in_labor_force,
                "citation": citation.to_reference_string(),
                "citation_id": citation.citation_id,
            }

            # Add to conversation
            if conversation_id and self.enable_memory:
                conversation = self.memory.get_conversation(conversation_id)
                if conversation:
                    summary = f"Retrieved employment data for {geography} ({year})"
                    conversation.add_message(
                        MessageRole.ASSISTANT,
                        summary,
                        citations=[citation.citation_id],
                        metadata={"insights": insights}
                    )

            return insights

        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Close all connections."""
        self.client.close()
