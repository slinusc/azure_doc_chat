"""
Configuration management for Azure RAG Application
Unified naming convention for all Azure services
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with unified Azure service naming"""

    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # ============================================
    # AZURE BLOB STORAGE - Document Storage
    # ============================================
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'documents')

    # ============================================
    # AZURE OPENAI - Embeddings Service
    # ============================================
    AZURE_OPENAI_EMBEDDINGS_ENDPOINT = os.getenv('AZURE_OPENAI_EMBEDDINGS_ENDPOINT')
    AZURE_OPENAI_EMBEDDINGS_API_KEY = os.getenv('AZURE_OPENAI_EMBEDDINGS_API_KEY')
    AZURE_OPENAI_EMBEDDINGS_MODEL = os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL', 'text-embedding-3-small')

    # ============================================
    # AZURE DOCUMENT INTELLIGENCE - PDF Extraction
    # ============================================
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    AZURE_DOCUMENT_INTELLIGENCE_API_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_API_KEY')

    # ============================================
    # AZURE OPENAI - Language Model (Chat)
    # ============================================
    AZURE_OPENAI_LLM_ENDPOINT = os.getenv('AZURE_OPENAI_LLM_ENDPOINT')
    AZURE_OPENAI_LLM_API_KEY = os.getenv('AZURE_OPENAI_LLM_API_KEY')
    AZURE_OPENAI_LLM_MODEL = os.getenv('AZURE_OPENAI_LLM_MODEL', 'gpt-5-nano')

    # ============================================
    # AZURE COGNITIVE SEARCH - Vector Search
    # ============================================
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
    AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME', 'rag-index')

    @classmethod
    def validate_config(cls):
        """
        Validate that all required configuration variables are set
        Raises ValueError if any required config is missing
        """
        required_config = [
            'AZURE_STORAGE_CONNECTION_STRING',
            'AZURE_OPENAI_EMBEDDINGS_ENDPOINT',
            'AZURE_OPENAI_EMBEDDINGS_API_KEY',
            'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT',
            'AZURE_DOCUMENT_INTELLIGENCE_API_KEY',
            'AZURE_OPENAI_LLM_ENDPOINT',
            'AZURE_OPENAI_LLM_API_KEY',
            'AZURE_SEARCH_ENDPOINT',
            'AZURE_SEARCH_API_KEY',
        ]

        missing = [key for key in required_config if not getattr(cls, key)]
        if missing:
            raise ValueError(
                f'Missing required configuration: {", ".join(missing)}'
            )
