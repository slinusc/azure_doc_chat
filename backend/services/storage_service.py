"""
Azure Blob Storage Service
Handles uploading, downloading, and managing PDF documents
"""

import logging
from azure.storage.blob import BlobServiceClient
from utils.config import Config

logger = logging.getLogger(__name__)


class StorageService:
    """Service for interacting with Azure Blob Storage"""

    def __init__(self):
        """Initialize Blob Storage client using connection string"""
        # Create client from connection string
        self.blob_service_client = BlobServiceClient.from_connection_string(
            Config.AZURE_STORAGE_CONNECTION_STRING
        )

        self.container_name = Config.AZURE_STORAGE_CONTAINER_NAME
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

    def upload_pdf(self, file_name: str, file_data: bytes) -> str:
        """
        Upload a PDF file to Blob Storage

        Args:
            file_name: Name of the file (should be unique)
            file_data: Binary file data

        Returns:
            Blob URL of the uploaded file
        """
        try:
            logger.info(f"Uploading PDF: {file_name}")

            # Upload blob
            blob_client = self.container_client.upload_blob(
                name=file_name,
                data=file_data,
                overwrite=True
            )

            logger.info(f"Successfully uploaded: {file_name}")
            return blob_client.url

        except Exception as e:
            logger.error(f"Error uploading PDF {file_name}: {str(e)}")
            raise

    def download_pdf(self, file_name: str) -> bytes:
        """
        Download a PDF file from Blob Storage

        Args:
            file_name: Name of the file to download

        Returns:
            Binary file data
        """
        try:
            logger.info(f"Downloading PDF: {file_name}")

            blob_client = self.container_client.get_blob_client(file_name)
            download_stream = blob_client.download_blob()
            file_data = download_stream.readall()

            logger.info(f"Successfully downloaded: {file_name}")
            return file_data

        except Exception as e:
            logger.error(f"Error downloading PDF {file_name}: {str(e)}")
            raise

    def delete_pdf(self, file_name: str) -> None:
        """
        Delete a PDF file from Blob Storage

        Args:
            file_name: Name of the file to delete
        """
        try:
            logger.info(f"Deleting PDF: {file_name}")

            blob_client = self.container_client.get_blob_client(file_name)
            blob_client.delete_blob()

            logger.info(f"Successfully deleted: {file_name}")

        except Exception as e:
            logger.error(f"Error deleting PDF {file_name}: {str(e)}")
            raise

    def list_pdfs(self) -> list:
        """
        List all PDF files in the container

        Returns:
            List of dicts with blob metadata (name, size, url)
        """
        try:
            blobs = self.container_client.list_blobs()
            pdf_list = []
            for blob in blobs:
                pdf_list.append({
                    'name': blob.name,
                    'size': blob.size,
                    'url': self.get_blob_url(blob.name)
                })
            logger.info(f"Listed {len(pdf_list)} PDFs in storage")
            return pdf_list

        except Exception as e:
            logger.error(f"Error listing PDFs: {str(e)}")
            raise

    def get_blob_url(self, file_name: str) -> str:
        """
        Get the public URL of a blob

        Args:
            file_name: Name of the blob

        Returns:
            Public URL of the blob
        """
        blob_client = self.container_client.get_blob_client(file_name)
        return blob_client.url


# Create a singleton instance
storage_service = StorageService()
