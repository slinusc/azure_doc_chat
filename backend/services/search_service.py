"""
Azure Cognitive Search Service
Handles indexing and searching document chunks with vector embeddings
"""

import logging
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.core.credentials import AzureKeyCredential
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import Config

logger = logging.getLogger(__name__)


class SearchService:
    """Service for managing Azure Cognitive Search"""

    def __init__(self):
        """Initialize Cognitive Search client"""
        self.endpoint = Config.AZURE_SEARCH_ENDPOINT
        self.api_key = Config.AZURE_SEARCH_API_KEY
        self.index_name = Config.AZURE_SEARCH_INDEX_NAME

        self.credentials = AzureKeyCredential(self.api_key)

        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credentials
        )

        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credentials
        )

        logger.info(f"SearchService initialized with index: {self.index_name}")

    def create_index(self):
        """Create the search index with vector search capability"""
        try:
            logger.info(f"Creating index: {self.index_name}")

            # Delete existing index if it exists
            try:
                self.index_client.delete_index(self.index_name)
                logger.info(f"Deleted existing index: {self.index_name}")
            except Exception as e:
                logger.warning(f"Index does not exist or could not be deleted: {str(e)}")

            index = SearchIndex(
                name=self.index_name,
                fields=[
                    SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True),
                    SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="document_name", type=SearchFieldDataType.String, filterable=True),
                    SimpleField(name="chunk_index", type=SearchFieldDataType.Int32, sortable=True),
                    SimpleField(name="page_number", type=SearchFieldDataType.Int32),
                    SearchableField(name="chunk_text", type=SearchFieldDataType.String, searchable=True, retrievable=True),
                    SearchField(
                        name="text_vector",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=1536,
                        vector_search_profile_name="myHnswProfile"
                    ),
                    SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
                ],
                vector_search=VectorSearch(
                    algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
                    profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw")]
                )
            )

            result = self.index_client.create_or_update_index(index)
            logger.info(f"Index '{self.index_name}' created/updated successfully")
            return result

        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise

    def index_chunks(self, document_id: str, document_name: str, chunks: list, embeddings: list):
        """Index document chunks with their embeddings"""
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks must match number of embeddings")

            logger.info(f"Indexing {len(chunks)} chunks for document: {document_name}")

            documents = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc = {
                    "id": f"{document_id}_{i}",
                    "document_id": document_id,
                    "document_name": document_name,
                    "chunk_index": chunk.get("chunk_index", i) if isinstance(chunk, dict) else i,
                    "page_number": chunk.get("page_number", 0) if isinstance(chunk, dict) else 0,
                    "chunk_text": chunk.get("text", chunk) if isinstance(chunk, dict) else chunk,
                    "text_vector": embedding,
                    "created_at": chunk.get("created_at", None) if isinstance(chunk, dict) else None
                }
                documents.append(doc)

            result = self.search_client.upload_documents(documents)
            logger.info(f"Successfully indexed {len(documents)} chunks")

            return [f"{document_id}_{i}" for i in range(len(chunks))]

        except Exception as e:
            logger.error(f"Error indexing chunks: {str(e)}")
            raise

    def search_chunks(self, query_embedding: list, top_k: int = 5, filters: str = None):
        """Search for relevant chunks using vector similarity"""
        try:
            logger.info(f"Searching for top {top_k} similar chunks")

            # Use REST API directly for vector search due to SDK limitations
            import requests
            import json

            # Build the search request body - note: all fields must be strings, not arrays
            search_request = {
                "search": "",
                "queryType": "semantic",
                "semanticConfiguration": "default",
                "vectorQueries": [
                    {
                        "vector": query_embedding,
                        "k": top_k,
                        "fields": "text_vector",
                        "kind": "vector"
                    }
                ],
                "select": "id,document_id,document_name,chunk_text,page_number,chunk_index",
            }

            if filters:
                search_request["filter"] = filters

            # Make REST API call
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }

            url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version=2023-11-01"

            logger.info(f"Calling Azure Search REST API: {url}")
            response = requests.post(url, headers=headers, json=search_request)

            if response.status_code != 200:
                logger.error(f"Search API returned status {response.status_code}: {response.text}")
                response.raise_for_status()

            response_data = response.json()

            search_results = []
            for result in response_data.get("value", []):
                search_results.append({
                    "id": result["id"],
                    "document_id": result.get("document_id"),
                    "document_name": result.get("document_name"),
                    "chunk_text": result.get("chunk_text"),
                    "page_number": result.get("page_number"),
                    "chunk_index": result.get("chunk_index"),
                    "score": result.get("@search.score")
                })

            logger.info(f"Found {len(search_results)} relevant chunks")
            return search_results

        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            raise

    def delete_chunks(self, document_id: str):
        """Delete all chunks for a document by document ID"""
        try:
            logger.info(f"Deleting chunks for document: {document_id}")
            self.search_client.delete_documents(
                documents=[{"id": f"{document_id}_{i}"} for i in range(1000)]
            )
            logger.info(f"Deleted chunks for document: {document_id}")

        except Exception as e:
            logger.error(f"Error deleting chunks: {str(e)}")
            raise

    def delete_chunks_by_name(self, document_name: str):
        """Delete all chunks for a document by document name using REST API filter"""
        try:
            import requests

            logger.info(f"Deleting chunks for document: {document_name}")

            # Build the delete request using REST API with filter
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }

            # Use the search API with a filter to get all matching documents, then delete them
            url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version=2023-11-01"

            # First, search for all documents with this name
            # Note: Azure Search filters use single quotes for literal string values
            search_request = {
                "search": "*",
                "filter": f"document_name eq '{document_name}'",
                "select": "id",
                "top": 10000
            }

            logger.debug(f"Search URL: {url}")
            logger.debug(f"Search request: {search_request}")

            response = requests.post(url, headers=headers, json=search_request, timeout=60)

            if response.status_code != 200:
                logger.error(f"Search failed with status {response.status_code}: {response.text}")
                response.raise_for_status()

            search_results = response.json()
            logger.debug(f"Search results: {search_results}")

            doc_ids_to_delete = []

            # Extract IDs from search results
            for result in search_results.get("value", []):
                doc_ids_to_delete.append({"id": result["id"]})

            logger.info(f"Found {len(doc_ids_to_delete)} chunks to delete for document: {document_name}")

            if doc_ids_to_delete:
                # Delete all found documents using the SDK instead of REST API
                logger.debug(f"Deleting {len(doc_ids_to_delete)} documents from index")

                result = self.search_client.delete_documents(doc_ids_to_delete)

                logger.info(f"Successfully deleted {len(doc_ids_to_delete)} chunks for document: {document_name}")
            else:
                logger.warning(f"No chunks found for document: {document_name}")

        except Exception as e:
            logger.error(f"Error deleting chunks by name: {str(e)}")
            raise

    def get_index_stats(self):
        """Get statistics about the index"""
        try:
            stats = self.index_client.get_index_statistics(self.index_name)
            return {
                "document_count": stats.document_count,
                "storage_size": stats.storage_size
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            raise


search_service = SearchService()


if __name__ == "__main__":

    import embedding_service

    embedding_service = embedding_service.EmbeddingService()
    query = embedding_service.embed_chunks(["What is GAIA?"])
    chunks = search_service.search_chunks(query_embedding=query[0], top_k=3)
    for chunk in chunks:
        print(f"Document: {chunk['document_name']}, Score: {chunk['score']}\nText: {chunk['chunk_text']}\n")