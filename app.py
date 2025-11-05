"""
Azure RAG Application - Flask Backend
Main application entry point
"""

from flask import Flask, send_from_directory, request
from flask_cors import CORS
import logging
import os
import sys

# Add backend directory to path for imports to work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from utils.config import Config
from routes import documents_bp, chat_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path to frontend directory (relative to this file)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')


def create_app():
    """
    Create and configure the Flask application
    """
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

    # Load configuration
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints (route modules)
    app.register_blueprint(documents_bp)
    app.register_blueprint(chat_bp)

    # Serve static files (CSS, JS)
    @app.route('/css/<path:path>')
    def send_css(path):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), path)

    @app.route('/js/<path:path>')
    def send_js(path):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), path)

    @app.route('/assets/<path:path>')
    def send_assets(path):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), path)

    # Serve index.html for root path
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'service': 'azure-rag-backend'
        }, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # For API routes, return JSON error
        if request.path.startswith('/api/'):
            return {
                'error': 'Not Found',
                'message': 'The requested endpoint does not exist'
            }, 404
        # For everything else, serve index.html (for frontend routing)
        return send_from_directory(FRONTEND_DIR, 'index.html'), 200

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal Server Error: {error}')
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }, 500

    logger.info('Flask application created successfully')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
