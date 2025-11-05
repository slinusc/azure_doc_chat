"""
Chat endpoint for RAG-based Q&A
Handles user queries and returns context-aware responses using vector search and LLM
Supports streaming responses for better UX
"""

from flask import Blueprint, request, jsonify, Response
import logging
import json
from services import embedding_service, search_service, llm_service

chat_bp = Blueprint('chat', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


def build_context_from_results(search_results: list) -> str:
    """
    Build context string from search results for LLM prompt

    Args:
        search_results: List of search result dicts from Cognitive Search

    Returns:
        Formatted context string with relevant chunks
    """
    if not search_results:
        return "No relevant documents found in the knowledge base."

    context = "Based on the following documents:\n\n"

    for i, result in enumerate(search_results, 1):
        doc_name = result.get('document_name', 'Unknown')
        chunk_text = result.get('chunk_text', '')
        page_num = result.get('page_number', 'N/A')
        score = result.get('score', 0)

        context += f"[Document {i}: {doc_name}, Page {page_num}, Relevance: {score:.2f}]\n"
        context += f"{chunk_text[:500]}...\n\n" if len(chunk_text) > 500 else f"{chunk_text}\n\n"

    return context


def generate_streaming_response(query, search_results, context):
    """
    Generator function that yields streaming chunks for Server-Sent Events (SSE)

    Args:
        query: User's query
        search_results: Search results from Cognitive Search
        context: Built context from search results

    Yields:
        JSON strings for streaming response
    """
    try:
        # First, yield metadata about the response
        yield json.dumps({
            'type': 'metadata',
            'query': query,
            'results_count': len(search_results)
        }) + '\n'

        # Generate response using LLM
        if not search_results:
            response_text = f"I couldn't find relevant information in the uploaded documents to answer: \"{query}\"\n\nPlease try uploading more documents or reformulating your question."
            logger.info('No search results found, returning default response')
        else:
            logger.info('Generating response using LLM with streaming...')
            response_text = llm_service.generate_response(query, context)
            logger.info('Response generated successfully by LLM')

        # Stream the response text character by character for smooth display
        for char in response_text:
            yield json.dumps({
                'type': 'chunk',
                'content': char
            }) + '\n'

        # Finally, yield the sources (deduplicated by document and page)
        # Use a dict to track seen (document_name, page_number) combinations
        seen_sources = {}
        sources = []
        for result in search_results:
            doc_name = result.get('document_name')
            page_num = result.get('page_number', 'Unknown')

            if doc_name:
                source_key = (doc_name, page_num)

                # Only add if we haven't seen this document+page combination yet
                if source_key not in seen_sources:
                    seen_sources[source_key] = True
                    sources.append({
                        'document_name': doc_name,
                        'relevance_score': result.get('score', 0),
                        'page_number': page_num,
                        'chunk_text': result.get('chunk_text', '')
                    })

        yield json.dumps({
            'type': 'sources',
            'sources': sources
        }) + '\n'

        yield json.dumps({
            'type': 'done'
        }) + '\n'

    except Exception as e:
        logger.error(f'Error in streaming response: {str(e)}', exc_info=True)
        yield json.dumps({
            'type': 'error',
            'message': str(e)
        }) + '\n'


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Process a user query using RAG (Retrieval-Augmented Generation) with streaming
    Expects: JSON body with 'query' field
    Returns: Server-Sent Events stream with response chunks and sources

    RAG Pipeline:
    1. Generate embedding for user query using Azure AI Foundry Embeddings
    2. Search Cognitive Search index for top-k relevant PDF chunks using vector similarity
    3. Build context from retrieved chunks
    4. Generate response using Azure AI Foundry LLM with retrieved context
    5. Stream response chunks and return source references
    """
    try:
        # Parse request body
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Please provide a query in the request body'
            }), 400

        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)  # Allow customizing number of results

        if not query:
            return jsonify({
                'error': 'Empty query',
                'message': 'Please provide a non-empty query'
            }), 400

        logger.info(f'Processing chat query: {query[:100]}...')

        # Step 1: Generate embedding for the query
        logger.info('Generating embedding for query...')
        query_embedding = embedding_service.embed_text(query)
        logger.info(f'Generated query embedding with {len(query_embedding)} dimensions')

        # Step 2: Search for relevant chunks using vector similarity
        logger.info(f'Searching for top {top_k} relevant chunks...')
        search_results = search_service.search_chunks(query_embedding, top_k=top_k)
        logger.info(f'Found {len(search_results)} relevant chunks')

        # Step 3: Build context from search results
        context = build_context_from_results(search_results)

        # Return streaming response
        return Response(
            generate_streaming_response(query, search_results, context),
            mimetype='application/x-ndjson'
        )

    except Exception as e:
        logger.error(f'Error processing chat query: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Failed to process query',
            'message': str(e)
        }), 500
