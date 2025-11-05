"""
Routes package for Azure RAG Application
"""

from .documents import documents_bp
from .chat import chat_bp

__all__ = ['documents_bp', 'chat_bp']
