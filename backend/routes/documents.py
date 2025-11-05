"""
Document management routes
Handles document upload, retrieval, and deletion
"""

from flask import Blueprint, request, jsonify, send_file
from urllib.parse import unquote
import logging
import os
import uuid
import io
from services import storage_service, search_service, embedding_service, pdf_processor

documents_bp = Blueprint('documents', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@documents_bp.route('/documents', methods=['GET'])
def get_documents():
    """
    Get list of all uploaded documents from Azure Blob Storage
    Returns: List of documents with metadata (name, size, url)
    """
    try:
        logger.info("Retrieving documents from Azure Blob Storage...")
        blob_documents = storage_service.list_pdfs()

        return jsonify({
            'documents': blob_documents,
            'count': len(blob_documents)
        }), 200

    except Exception as e:
        logger.error(f'Error retrieving documents: {str(e)}')
        return jsonify({
            'error': 'Failed to retrieve documents',
            'message': str(e)
        }), 500


@documents_bp.route('/documents', methods=['POST'])
def upload_document():
    """
    Upload a new PDF document
    Accepts: File in multipart form data
    Returns: Document metadata and upload status

    Process:
    1. Save PDF to Azure Blob Storage
    2. Extract text from PDF
    3. Chunk text into smaller pieces
    4. Generate embeddings for each chunk
    5. Index chunks in Cognitive Search
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please upload a PDF file'
            }), 400

        file = request.files['file']

        # Validate file
        if file.filename == '':
            return jsonify({
                'error': 'Invalid file',
                'message': 'Please select a file'
            }), 400

        # Check file extension - only PDF
        allowed_extensions = {'.pdf'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': 'Invalid file type',
                'message': 'Please upload a PDF file'
            }), 400

        # Read file data
        file_data = file.read()
        file_size = len(file_data)

        try:
            # Generate a unique document ID
            document_id = str(uuid.uuid4())

            # Step 1: Upload PDF to Azure Blob Storage
            logger.info(f'Uploading {file.filename} to Blob Storage...')
            blob_url = storage_service.upload_pdf(file.filename, file_data)
            logger.info(f'Successfully uploaded to Blob Storage: {blob_url}')

            # Step 2: Extract text from PDF
            logger.info(f'Extracting text from {file.filename}...')
            pdf_text = pdf_processor.extract_text(file_data)

            # Step 3: Chunk text into smaller pieces
            logger.info(f'Chunking text...')
            chunks = pdf_processor.chunk_text(pdf_text)

            # Step 4: Generate embeddings for each chunk
            logger.info(f'Generating embeddings for {len(chunks)} chunks...')
            # Extract just the text from chunk dicts for embedding
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = embedding_service.embed_chunks(chunk_texts)
            logger.info(f'Generated {len(embeddings)} embeddings')

            # Step 5: Index chunks in Cognitive Search
            logger.info(f'Indexing chunks in Cognitive Search...')
            search_service.index_chunks(
                document_id=document_id,
                document_name=file.filename,
                chunks=chunks,
                embeddings=embeddings
            )
            logger.info(f'Successfully indexed {len(chunks)} chunks')

            logger.info(f'PDF processed successfully: {file.filename} (ID: {document_id})')

            # Return document info
            return jsonify({
                'message': 'PDF uploaded and indexed successfully.',
                'document': {
                    'id': document_id,
                    'name': file.filename,
                    'size': file_size,
                    'url': blob_url,
                    'chunks': len(chunks)
                }
            }), 201

        except Exception as upload_error:
            logger.error(f'Error uploading to Blob Storage: {str(upload_error)}')
            raise

    except Exception as e:
        logger.error(f'Error uploading PDF: {str(e)}')
        return jsonify({
            'error': 'Upload failed',
            'message': str(e)
        }), 500


@documents_bp.route('/documents/<filename>', methods=['DELETE'])
def delete_document(filename):
    """
    Delete a document by filename
    Deletes from:
    1. Azure Blob Storage
    2. Cognitive Search index

    Args: filename - Name of the document file to delete (URL encoded)
    Returns: Deletion status
    """
    try:
        # Decode the filename from URL encoding
        filename = unquote(filename)

        # Step 1: Delete from Azure Blob Storage
        try:
            logger.info(f'Deleting {filename} from Blob Storage...')
            storage_service.delete_pdf(filename)
            logger.info(f'Successfully deleted from Blob Storage: {filename}')
        except Exception as blob_error:
            logger.error(f'Error deleting from Blob Storage: {str(blob_error)}')
            # Continue with deletion even if blob deletion fails
            pass

        # Step 2: Delete from Cognitive Search index (delete by document name)
        try:
            logger.info(f'Deleting chunks from Cognitive Search for document: {filename}')
            search_service.delete_chunks_by_name(filename)
            logger.info(f'Successfully deleted chunks from Cognitive Search')
        except Exception as search_error:
            logger.error(f'Error deleting from Cognitive Search: {str(search_error)}')
            # Continue with deletion even if search deletion fails
            pass

        logger.info(f'Document deleted: {filename}')

        return jsonify({
            'message': 'Document deleted successfully',
            'filename': filename
        }), 200

    except Exception as e:
        logger.error(f'Error deleting document: {str(e)}')
        return jsonify({
            'error': 'Deletion failed',
            'message': str(e)
        }), 500


@documents_bp.route('/documents/<filename>/page/<int:page_number>', methods=['GET'])
def get_pdf_page(filename, page_number):
    """
    Get a specific page from a PDF as an image
    Returns: PNG image of the specified page
    """
    try:
        filename = unquote(filename)
        logger.info(f'Retrieving page {page_number} from {filename}...')

        # Download PDF from Blob Storage
        pdf_data = storage_service.download_pdf(filename)

        if not pdf_data:
            return jsonify({
                'error': 'Document not found',
                'message': f'Could not download {filename}'
            }), 404

        # Convert PDF page to image
        try:
            import fitz  # PyMuPDF
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

            if page_number < 1 or page_number > len(pdf_document):
                return jsonify({
                    'error': 'Invalid page number',
                    'message': f'Page {page_number} does not exist (total: {len(pdf_document)})'
                }), 400

            # Get the page (0-indexed)
            page = pdf_document[page_number - 1]

            # Render page to image with good quality
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            image_bytes = pix.tobytes(fmt="png")

            pdf_document.close()

            return send_file(
                io.BytesIO(image_bytes),
                mimetype='image/png',
                as_attachment=False
            )

        except ImportError:
            logger.error("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
            return jsonify({
                'error': 'PDF rendering not available',
                'message': 'PDF to image conversion requires PyMuPDF library'
            }), 500

    except Exception as e:
        logger.error(f'Error retrieving PDF page: {str(e)}')
        return jsonify({
            'error': 'Failed to retrieve PDF page',
            'message': str(e)
        }), 500
