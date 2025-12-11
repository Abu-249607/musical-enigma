"""Vector store for Census employment data chunks."""

from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings


class CensusVectorStore:
    """ChromaDB-based vector store for Census data.

    Stores chunked employment data with embeddings for
    semantic search and RAG retrieval.
    """

    def __init__(
        self,
        persist_dir: str | Path = "data/vectordb",
        collection_name: str = "census_employment",
    ):
        """Initialize the vector store.

        Args:
            persist_dir: Directory to persist the database
            collection_name: Name of the ChromaDB collection
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB with persistence
        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Census Bureau employment data chunks"},
        )

    def add_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """Add data chunks to the vector store.

        Args:
            chunks: List of chunk dictionaries from DataChunker

        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["id"])
            documents.append(chunk["embedding_text"])

            # Flatten metadata for ChromaDB (only primitive types)
            flat_metadata = {
                "type": chunk["type"],
                "geography_name": chunk["metadata"]["geography_name"],
                "geography_level": chunk["metadata"].get("geography_level", ""),
                "year": chunk["metadata"]["year"],
                "citation_id": chunk["metadata"]["citation_id"],
                "dataset": chunk["metadata"].get("dataset", ""),
                "content": chunk["content"][:1000],  # Truncate for storage
            }

            # Add structured data as JSON string
            if chunk.get("structured_data"):
                import json
                flat_metadata["structured_data_json"] = json.dumps(
                    chunk["structured_data"]
                )

            metadatas.append(flat_metadata)

        # Upsert to handle duplicates
        self._collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_geography: str | None = None,
        filter_year: int | None = None,
        filter_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for relevant chunks.

        Args:
            query: Search query
            n_results: Maximum number of results
            filter_geography: Filter by geography name
            filter_year: Filter by year
            filter_type: Filter by chunk type

        Returns:
            List of matching chunks with scores
        """
        # Build where clause
        where = {}
        if filter_geography:
            where["geography_name"] = filter_geography
        if filter_year:
            where["year"] = filter_year
        if filter_type:
            where["type"] = filter_type

        # Execute search
        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                import json

                metadata = results["metadatas"][0][i]
                structured_data = None
                if metadata.get("structured_data_json"):
                    structured_data = json.loads(metadata["structured_data_json"])

                formatted.append({
                    "id": chunk_id,
                    "content": metadata.get("content", ""),
                    "document": results["documents"][0][i],
                    "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": {
                        "type": metadata.get("type"),
                        "geography_name": metadata.get("geography_name"),
                        "geography_level": metadata.get("geography_level"),
                        "year": metadata.get("year"),
                        "citation_id": metadata.get("citation_id"),
                        "dataset": metadata.get("dataset"),
                    },
                    "structured_data": structured_data,
                })

        return formatted

    def search_by_geography(
        self,
        geography_name: str,
        n_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Get all chunks for a specific geography."""
        return self.search(
            query=f"employment data for {geography_name}",
            n_results=n_results,
            filter_geography=geography_name,
        )

    def search_comparative(
        self,
        geographies: list[str],
        metric: str = "unemployment",
        n_results: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for data to compare multiple geographies."""
        query = f"Compare {metric} rates across {', '.join(geographies)}"
        return self.search(query=query, n_results=n_results)

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_chunks": self._collection.count(),
            "collection_name": self._collection.name,
            "persist_directory": str(self.persist_dir),
        }

    def clear(self) -> int:
        """Clear all data from the collection."""
        count = self._collection.count()
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.create_collection(
            name=self._collection.name,
            metadata={"description": "Census Bureau employment data chunks"},
        )
        return count

    def delete_by_geography(self, geography_name: str) -> int:
        """Delete all chunks for a specific geography."""
        # Get IDs to delete
        results = self._collection.get(
            where={"geography_name": geography_name},
            include=["metadatas"],
        )

        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            return len(results["ids"])
        return 0
