"""
PDF Processing Service using Azure AI Document Intelligence
Handles text extraction and chunking from PDF files
"""

import logging
import os
import sys
import tempfile
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for processing PDF documents using Azure AI Document Intelligence with LangChain"""

    def __init__(self):
        """Initialize the PDF processor with Azure AI Document Intelligence credentials"""
        self.endpoint = Config.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
        self.api_key = Config.AZURE_DOCUMENT_INTELLIGENCE_API_KEY

        # Headers to split on for markdown-based chunking
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        if self.endpoint and self.api_key:
            logger.info("PDFProcessor initialized with Azure AI Document Intelligence")
        else:
            logger.warning("PDFProcessor initialized without Azure AI Document Intelligence credentials")

    def extract_text(self, file_data: bytes) -> str:
        """
        Extract text from a PDF file using Azure AI Document Intelligence.
        Saves bytes to temporary file and uses AzureAIDocumentIntelligenceLoader.

        Args:
            file_data (bytes): The binary data of the PDF file.

        Returns:
            str: The extracted text from the PDF file (markdown format).
        """
        try:
            if not self.endpoint or not self.api_key:
                raise RuntimeError("Azure AI Document Intelligence credentials not configured.")

            logger.info("Extracting text from PDF using Azure AI Document Intelligence...")

            # Save bytes to temporary file (loader requires file_path)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(file_data)
                tmp_file_path = tmp_file.name

            try:
                # Use LangChain's loader for cleaner API
                loader = AzureAIDocumentIntelligenceLoader(
                    file_path=tmp_file_path,
                    api_key=self.api_key,
                    api_endpoint=self.endpoint,
                    api_model="prebuilt-layout"
                )

                docs = loader.load()

                if not docs:
                    raise ValueError("No content extracted from PDF")

                # Get markdown content from first document
                markdown_content = docs[0].page_content

                logger.info(f"Extracted {len(markdown_content)} characters from PDF")
                return markdown_content

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def chunk_text(self, text: str) -> list:
        """
        Chunk text into semantic chunks using markdown headers and figure boundaries.
        Treats <figure> tags as semantic boundaries to keep figures with their content.

        Args:
            text (str): The text to be chunked (markdown format from Document Intelligence).

        Returns:
            list: A list of text chunks split by markdown headers and figure tags.
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            logger.info("Chunking text using markdown headers and figure boundaries...")

            import re

            # Pre-process: Add markdown header markers before <figure> tags to force splits
            # This treats figures as semantic boundaries
            text = re.sub(
                r'(\n)(<figure>)',
                r'\1### Figure\n\2',
                text,
                flags=re.MULTILINE
            )

            # Use markdown-based splitting - respects document structure
            text_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=self.headers_to_split_on,
                return_each_line=False
            )

            splits = text_splitter.split_text(text)

            # Extract content and metadata from Document objects
            chunks = []
            current_page = 1
            chunk_index = 0

            # Secondary splitter for chunks that are too large for embeddings model
            # Text-embedding-3-small has max 8192 tokens (~30KB characters)
            secondary_splitter = RecursiveCharacterTextSplitter(
                chunk_size=6000,  # Conservative size in characters
                chunk_overlap=500,
                separators=["\n\n", "\n", ". ", " ", ""]
            )

            for idx, split in enumerate(splits):
                # Count page breaks before this chunk to determine current page
                # Each <!-- PageBreak --> marker indicates a new page
                text_before = text[:text.find(split.page_content)] if split.page_content in text else ""
                page_breaks_before = text_before.count('<!-- PageBreak -->')
                current_page = page_breaks_before + 1

                # If chunk is too large, split it further
                if len(split.page_content) > 6000:
                    logger.debug(f"Chunk {idx} is {len(split.page_content)} chars, splitting further...")
                    sub_chunks = secondary_splitter.split_text(split.page_content)
                    for sub_chunk in sub_chunks:
                        chunk_dict = {
                            'text': sub_chunk,
                            'page_number': current_page,
                            'chunk_index': chunk_index
                        }
                        chunks.append(chunk_dict)
                        chunk_index += 1
                else:
                    chunk_dict = {
                        'text': split.page_content,
                        'page_number': current_page,
                        'chunk_index': chunk_index
                    }
                    chunks.append(chunk_dict)
                    chunk_index += 1

            if chunks:
                logger.info(f"Created {len(chunks)} chunks using markdown headers and figure boundaries")
                logger.debug(f"Chunk sizes: min={min(len(c['text']) for c in chunks)}, "
                           f"max={max(len(c['text']) for c in chunks)}, "
                           f"avg={sum(len(c['text']) for c in chunks) / len(chunks):.0f} characters")
            else:
                # If no headers found, return whole text as single chunk
                logger.warning("No markdown headers found, returning text as single chunk")
                chunks = [{'text': text, 'page_number': 1, 'chunk_index': 0}]

            return chunks

        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise


# Create singleton instance
pdf_processor = PDFProcessor()

if __name__ == "__main__":
    # Example usage
    with open("C:/Users/linus/OneDrive/Freelance_Software_Projects/azure_rag_app/2505.06371v1.pdf", "rb") as f:
        pdf_data = f.read()

    extracted_text = pdf_processor.extract_text(pdf_data)
    text_chunks = pdf_processor.chunk_text(extracted_text)

    for i, chunk in enumerate(text_chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print()