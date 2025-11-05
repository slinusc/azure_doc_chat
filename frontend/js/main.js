// Main application logic for RAG Chatbot

class ChatbotApp {
    constructor() {
        this.documents = [];
        this.isLoading = false;

        // DOM Elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.documentList = document.getElementById('documentList');
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.pdfPreviewPanel = document.getElementById('pdfPreviewPanel');
        this.closePdfPreviewBtn = document.getElementById('closePdfPreview');
        this.pdfPreviewContent = document.getElementById('pdfPreviewContent');

        // Initialize event listeners
        this.initializeEventListeners();

        // Load documents on page load
        this.loadDocuments();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Upload area events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Chat events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

    }

    /**
     * Open PDF preview with source content
     */
    openPdfPreview(fileName, pageNumber, content) {
        let htmlContent = `
            <div class="pdf-preview-info">
                <div class="pdf-preview-filename">${escapeHtml(fileName)}</div>
                <div class="pdf-preview-page">Page ${pageNumber || 'N/A'}</div>
            </div>
            <div class="pdf-preview-image" id="pdfPageImage">
                <p style="text-align: center; color: #999;">Loading PDF page...</p>
            </div>
        `;

        this.pdfPreviewContent.innerHTML = htmlContent;

        // Fetch and display the PDF page image
        if (pageNumber && pageNumber !== 'N/A') {
            const pageImageElement = document.getElementById('pdfPageImage');
            const encodedFileName = encodeURIComponent(fileName);
            const imageUrl = `/api/documents/${encodedFileName}/page/${pageNumber}`;

            fetch(imageUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to load page: ${response.statusText}`);
                    }
                    return response.blob();
                })
                .then(blob => {
                    const imageUrl = URL.createObjectURL(blob);
                    const imageElement = document.createElement('img');
                    imageElement.src = imageUrl;
                    imageElement.style.maxWidth = '100%';
                    imageElement.style.height = 'auto';
                    imageElement.style.borderRadius = '4px';
                    imageElement.onclick = () => openPdfModal(imageUrl);
                    pageImageElement.innerHTML = '';
                    pageImageElement.appendChild(imageElement);
                })
                .catch(error => {
                    console.error('Error loading PDF page:', error);
                    pageImageElement.innerHTML = `<p style="color: #d32f2f; text-align: center;">Failed to load PDF page: ${error.message}</p>`;
                });
        }
    }

    /**
     * Handle file selection from input
     * @param {Event} event - Change event
     */
    async handleFileSelect(event) {
        const files = Array.from(event.target.files);
        for (const file of files) {
            await this.uploadFile(file);
        }
        // Reset file input
        this.fileInput.value = '';
    }

    /**
     * Handle drag over event
     * @param {DragEvent} event - Drag event
     */
    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        this.uploadArea.classList.add('dragover');
    }

    /**
     * Handle drag leave event
     * @param {DragEvent} event - Drag event
     */
    handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        this.uploadArea.classList.remove('dragover');
    }

    /**
     * Handle drop event
     * @param {DragEvent} event - Drag event
     */
    async handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        this.uploadArea.classList.remove('dragover');

        const files = Array.from(event.dataTransfer.files);
        for (const file of files) {
            if (isValidFileType(file)) {
                await this.uploadFile(file);
            } else {
                showNotification(
                    `Invalid file type: ${file.name}. Please upload PDF files only.`,
                    'error'
                );
            }
        }
    }

    /**
     * Upload a PDF file to the backend
     * @param {File} file - PDF file to upload
     */
    async uploadFile(file) {
        if (!isValidFileType(file)) {
            showNotification(
                `Invalid file type: ${file.name}. Please upload PDF files only.`,
                'error'
            );
            return;
        }

        try {
            this.setLoading(true);
            showNotification(`Uploading ${file.name}...`, 'info');

            const response = await apiService.uploadDocument(file);

            showNotification(
                `Document "${file.name}" uploaded successfully!`,
                'success'
            );

            // Reload documents list
            await this.loadDocuments();
        } catch (error) {
            showNotification(
                `Failed to upload ${file.name}: ${error.message}`,
                'error'
            );
            console.error('Upload error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Load and display list of documents
     */
    async loadDocuments() {
        try {
            const response = await apiService.getDocuments();
            this.documents = response.documents || [];
            this.renderDocumentList();
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.documents = [];
            this.renderDocumentList();
        }
    }

    /**
     * Render the document list in the UI
     */
    renderDocumentList() {
        this.documentList.innerHTML = '';

        if (this.documents.length === 0) {
            this.documentList.innerHTML = '<p style="color: #999; text-align: center; padding: 1rem; font-size: 0.9rem;">No documents uploaded yet</p>';
            return;
        }

        this.documents.forEach((doc) => {
            const docEl = document.createElement('div');
            docEl.className = 'document-item';
            docEl.innerHTML = `
                <div class="document-info">
                    <div class="document-name">${escapeHtml(doc.name)}</div>
                    <div class="document-size">Size: ${formatFileSize(doc.size || 0)}</div>
                </div>
                <button class="delete-btn" onclick="chatbotApp.deleteDocument('${doc.name}')">Delete</button>
            `;
            this.documentList.appendChild(docEl);
        });
    }

    /**
     * Delete a document
     * @param {string} filename - Filename of document to delete
     */
    async deleteDocument(filename) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            this.setLoading(true);
            await apiService.deleteDocument(filename);
            showNotification('Document deleted successfully!', 'success');
            await this.loadDocuments();
        } catch (error) {
            showNotification(`Failed to delete document: ${error.message}`, 'error');
            console.error('Delete error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Send a chat message with streaming
     */
    async sendMessage() {
        const query = this.userInput.value.trim();

        if (!query) {
            return;
        }

        if (this.isLoading) {
            return;
        }

        try {
            // Add user message to chat
            this.addMessage(query, 'user');
            this.userInput.value = '';

            this.setLoading(true);

            // Create a message element for the assistant response (will be updated as it streams)
            const messageEl = document.createElement('div');
            messageEl.className = 'message assistant';

            const contentEl = document.createElement('div');
            contentEl.className = 'message-content';
            contentEl.textContent = '';  // Will be filled by streaming chunks

            const timestampEl = document.createElement('div');
            timestampEl.className = 'message-timestamp';
            timestampEl.textContent = formatTime(new Date());

            messageEl.appendChild(contentEl);
            messageEl.appendChild(timestampEl);

            this.chatMessages.appendChild(messageEl);

            // Auto-scroll to the new message
            scrollToBottom(this.chatMessages);

            let sources = [];

            // Use streaming API
            const response = await apiService.sendMessageStreaming(query, (chunk) => {
                if (chunk.type === 'chunk') {
                    // Update the content element with new character
                    contentEl.textContent += chunk.content;
                    scrollToBottom(this.chatMessages);
                } else if (chunk.type === 'sources') {
                    // Store sources for later use
                    sources = chunk.sources;
                } else if (chunk.type === 'done') {
                    // Response is complete, add sources section
                    if (sources.length > 0) {
                        const sourcesEl = document.createElement('div');
                        sourcesEl.className = 'message-sources';

                        const sourceTitle = document.createElement('div');
                        sourceTitle.className = 'sources-title';
                        sourceTitle.textContent = 'Sources';
                        sourcesEl.appendChild(sourceTitle);

                        sources.forEach((source) => {
                            const sourceItem = document.createElement('div');
                            sourceItem.className = 'source-item';
                            sourceItem.innerHTML = `
                                <div class="source-name">${escapeHtml(source.document_name || 'Unknown')}</div>
                                <div class="source-meta">Page ${source.page_number || 'N/A'}</div>
                            `;

                            // Add click handler to open PDF preview
                            sourceItem.addEventListener('click', () => {
                                this.openPdfPreview(
                                    source.document_name || 'Document',
                                    source.page_number || 'N/A',
                                    source.chunk_text || 'No content available'
                                );
                            });

                            sourcesEl.appendChild(sourceItem);
                        });

                        messageEl.appendChild(sourcesEl);
                        scrollToBottom(this.chatMessages);
                    }
                }
            });
        } catch (error) {
            this.addMessage(
                `Error: ${error.message}`,
                'error'
            );
            console.error('Chat error:', error);
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * Add a message to the chat display
     * @param {string} text - Message text
     * @param {string} role - Message role ('user', 'assistant', 'error')
     * @param {Array} sources - Array of source citations
     */
    addMessage(text, role = 'assistant', sources = null) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}`;

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.textContent = text;

        const timestampEl = document.createElement('div');
        timestampEl.className = 'message-timestamp';
        timestampEl.textContent = formatTime(new Date());

        messageEl.appendChild(contentEl);
        messageEl.appendChild(timestampEl);

        // Add sources if available and it's an assistant message
        if (sources && sources.length > 0 && role === 'assistant') {
            const sourcesEl = document.createElement('div');
            sourcesEl.className = 'message-sources';

            const sourceTitle = document.createElement('div');
            sourceTitle.className = 'sources-title';
            sourceTitle.textContent = 'Sources';
            sourcesEl.appendChild(sourceTitle);

            sources.forEach((source) => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                sourceItem.innerHTML = `
                    <div class="source-name">${escapeHtml(source.document_name || 'Unknown')}</div>
                    <div class="source-meta">Page ${source.page_number || 'N/A'}</div>
                `;

                // Add click handler to open PDF preview
                sourceItem.addEventListener('click', () => {
                    this.openPdfPreview(
                        source.document_name || 'Document',
                        source.page_number || 'N/A',
                        source.chunk_text || 'No content available'
                    );
                });

                sourcesEl.appendChild(sourceItem);
            });

            messageEl.appendChild(sourcesEl);
        }

        this.chatMessages.appendChild(messageEl);

        // Auto-scroll to bottom if user is already at bottom
        if (isScrolledToBottom(this.chatMessages)) {
            scrollToBottom(this.chatMessages);
        }
    }

    /**
     * Set loading state
     * @param {boolean} isLoading - Loading state
     */
    setLoading(isLoading) {
        this.isLoading = isLoading;
        this.sendButton.disabled = isLoading;
        this.fileInput.disabled = isLoading;

        if (isLoading) {
            this.sendButton.innerHTML = '<span class="loading-spinner"></span>';
        } else {
            this.sendButton.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16390963 C3.34915502,0.9 2.40734225,1.00636533 1.77946707,1.4776575 C0.994623095,2.10604706 0.837654326,3.0486314 1.15159189,3.99701575 L3.03521743,10.4380088 C3.03521743,10.5950566 3.34915502,10.5950566 3.50612381,10.5950566 L16.6915026,11.3805435 C16.6915026,11.3805435 17.1624089,11.3805435 17.1624089,11.7939826 L17.1624089,12.0510799 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z"></path>
                </svg>
            `;
        }
    }
}

/**
 * Open PDF page in fullscreen modal
 */
function openPdfModal(imageUrl) {
    const modal = document.getElementById('pdfModal');
    const modalImage = document.getElementById('pdfModalImage');
    modalImage.src = imageUrl;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Close PDF fullscreen modal
 */
function closePdfModal() {
    const modal = document.getElementById('pdfModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside the image
document.addEventListener('click', function(event) {
    const modal = document.getElementById('pdfModal');
    const modalContent = document.querySelector('.pdf-modal-content');
    if (modal && modal.classList.contains('active') && !modalContent.contains(event.target)) {
        closePdfModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closePdfModal();
    }
});

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbotApp = new ChatbotApp();
});
