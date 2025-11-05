// API Service for communicating with Flask backend

class ApiService {
    constructor() {
        // Configure API base URL based on environment
        this.baseURL = this.getBaseURL();
    }

    /**
     * Determine API base URL based on environment
     * @returns {string} Base URL for API
     */
    getBaseURL() {
        // Frontend and API are served from the same Flask server
        return `${window.location.protocol}//${window.location.host}`;
    }

    /**
     * Make a fetch request with error handling
     * @param {string} endpoint - API endpoint (e.g., '/api/chat')
     * @param {Object} options - Fetch options (method, headers, body, etc.)
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.message || `API Error: ${response.status} ${response.statusText}`
                );
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    /**
     * Upload a document to the backend
     * @param {File} file - File to upload
     * @returns {Promise<Object>} Upload response
     */
    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseURL}/api/documents`, {
                method: 'POST',
                body: formData,
                // Don't set Content-Type header - browser will set it with boundary
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.message || `Upload failed: ${response.status} ${response.statusText}`
                );
            }

            return await response.json();
        } catch (error) {
            console.error('Document Upload Error:', error);
            throw error;
        }
    }

    /**
     * Get list of uploaded documents
     * @returns {Promise<Object>} List of documents
     */
    async getDocuments() {
        return this.request('/api/documents', { method: 'GET' });
    }

    /**
     * Delete a document by filename
     * @param {string} filename - Filename to delete
     * @returns {Promise<Object>} Delete response
     */
    async deleteDocument(filename) {
        return this.request(`/api/documents/${encodeURIComponent(filename)}`, {
            method: 'DELETE',
        });
    }

    /**
     * Send a chat message and get a streaming response
     * @param {string} query - User query
     * @param {Function} onChunk - Callback for each chunk received
     * @returns {Promise<Object>} Full chat response with sources
     */
    async sendMessageStreaming(query, onChunk) {
        const url = `${this.baseURL}/api/chat`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.message || `API Error: ${response.status} ${response.statusText}`
                );
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let fullResponse = {
                response: '',
                sources: [],
                metadata: {}
            };

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');

                // Keep the last incomplete line in the buffer
                buffer = lines[lines.length - 1];

                // Process all complete lines
                for (let i = 0; i < lines.length - 1; i++) {
                    const line = lines[i].trim();
                    if (!line) continue;

                    try {
                        const chunk = JSON.parse(line);

                        if (chunk.type === 'metadata') {
                            fullResponse.metadata = chunk;
                            if (onChunk) onChunk(chunk);
                        } else if (chunk.type === 'chunk') {
                            fullResponse.response += chunk.content;
                            if (onChunk) onChunk(chunk);
                        } else if (chunk.type === 'sources') {
                            fullResponse.sources = chunk.sources;
                            if (onChunk) onChunk(chunk);
                        } else if (chunk.type === 'done') {
                            if (onChunk) onChunk(chunk);
                        } else if (chunk.type === 'error') {
                            throw new Error(chunk.message);
                        }
                    } catch (parseError) {
                        console.error('Error parsing chunk:', line, parseError);
                    }
                }
            }

            return fullResponse;
        } catch (error) {
            console.error('Streaming API Error:', error);
            throw error;
        }
    }
}

// Create a singleton instance
const apiService = new ApiService();
