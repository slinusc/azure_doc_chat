"""
Azure AI Foundry LLM Service
Generates chat responses using Azure AI Foundry models
"""

import logging
import requests
import json
from utils.config import Config

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using Azure AI Foundry LLM"""

    def __init__(self):
        """Initialize the LLM service"""
        self.endpoint = Config.AZURE_OPENAI_LLM_ENDPOINT
        self.api_key = Config.AZURE_OPENAI_LLM_API_KEY
        self.model = Config.AZURE_OPENAI_LLM_MODEL

        logger.info(f"LLMService initialized with model: {self.model}")

    def generate_response(self, query: str, context: str, max_tokens: int = 2000) -> str:
        """
        Generate a chat response using the LLM with provided context

        Args:
            query: User's question
            context: Retrieved document context from RAG
            max_tokens: Maximum tokens in response

        Returns:
            Generated response string
        """
        try:
            logger.info(f"Generating response for query: {query[:100]}...")

            # Build the system prompt with RAG context
            system_prompt = f"""You are a helpful assistant answering questions based on provided documents.

Use the following context from the documents to answer the user's question.
If the answer is not in the context, say you don't have enough information.

Context:
{context}"""

            # Build the request payload for Azure OpenAI
            # Using the OpenAI-compatible API format
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 1,  # gpt-5-nano only supports default temperature of 1
                "max_completion_tokens": max_tokens,
                "model": self.model
            }

            # Make request to Azure OpenAI endpoint
            # Azure OpenAI uses api-key header for authentication
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }

            # Use the endpoint directly (already contains the full path with api-version)
            url = self.endpoint
            logger.info(f"Calling LLM endpoint: {url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code != 200:
                logger.error(f"LLM API returned status {response.status_code}: {response.text}")
                response.raise_for_status()

            response_data = response.json()
            logger.info(f"LLM Response: {response_data}")

            # Extract the generated message
            if "choices" in response_data and len(response_data["choices"]) > 0:
                generated_text = response_data["choices"][0]["message"]["content"]
                logger.info(f"Response generated successfully: {generated_text[:100]}...")
                return generated_text
            else:
                logger.error(f"Unexpected response format: {response_data}")
                raise ValueError(f"Unexpected response format from LLM API")

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise


# Create singleton instance
llm_service = LLMService()
