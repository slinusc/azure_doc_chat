"""
Azure OpenAI Embeddings Service
Generates vector embeddings for text chunks
"""

import sys
import os
import logging

# Add parent directory to path for imports to work when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Azure OpenAI"""

    def __init__(self):
        """Initialize the embedding service"""
        self.endpoint = Config.AZURE_OPENAI_EMBEDDINGS_ENDPOINT
        self.api_key = Config.AZURE_OPENAI_EMBEDDINGS_API_KEY
        self.model = Config.AZURE_OPENAI_EMBEDDINGS_MODEL

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version="2024-02-15-preview",
            timeout=120.0  # Increase timeout to 2 minutes for large batches
        )

        logger.info(f"EmbeddingService initialized with model: {self.model}")

    def embed_chunks(self, chunks: list) -> list:
        """
        Generate embeddings for a list of text chunks

        Args:
            chunks (list): A list of text chunks to embed

        Returns:
            list: A list of embedding vectors
        """
        try:
            if not chunks:
                raise ValueError("Chunks list cannot be empty")

            logger.info(f"Generating embeddings for {len(chunks)} chunks...")

            embeddings = self.client.embeddings.create(
                input=chunks,
                model=self.model
            )

            embeddings_list = [data.embedding for data in embeddings.data]
            logger.info(f"Generated {len(embeddings_list)} embeddings")

            return embeddings_list

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def embed_text(self, text: str) -> list:
        """
        Generate embedding for a single text string

        Args:
            text (str): Text to embed

        Returns:
            list: Embedding vector
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            logger.info("Generating embedding for single text...")

            embeddings = self.client.embeddings.create(
                input=[text],
                model=self.model
            )

            embedding = embeddings.data[0].embedding
            logger.info("Generated single embedding")

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise


# Create singleton instance
embedding_service = EmbeddingService()


if __name__ == "__main__":
    service = EmbeddingService()
    sample_chunks = [
        "This is the first text chunk.",
        "This is the second text chunk."
    ]
    embeddings = service.embed_chunks(sample_chunks)
    for i, emb in enumerate(embeddings):
        print(f"Chunk {i+1} Embedding dimension: {len(emb)}")