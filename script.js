class ChatUI {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.fileInput = document.getElementById('fileInput');
        this.fileUploadBtn = document.getElementById('fileUploadBtn');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // File upload button click
        this.fileUploadBtn.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
        
        // Send button click
        this.sendBtn.addEventListener('click', () => {
            this.handleSendMessage();
        });
        
        // Enter key in chat input
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });
        
        // Drag and drop
        this.chatMessages.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.chatMessages.style.backgroundColor = '#f1f5f9';
        });
        
        this.chatMessages.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.chatMessages.style.backgroundColor = '#f8fafc';
        });
        
        this.chatMessages.addEventListener('drop', (e) => {
            e.preventDefault();
            this.chatMessages.style.backgroundColor = '#f8fafc';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    }
    
    handleFileUpload(file) {
        if (!file.type.match('image.*') && !file.type.match('video.*')) {
            this.addBotMessage('Please upload only images or videos.');
            return;
        }
        
        this.addUserFileMessage(file);
        
        if (file.type.match('image.*')) {
            this.analyzeImage(file);
        } else {
            this.addBotMessage('Video uploaded successfully! (Analysis would be implemented similarly)');
        }
        
        // Clear file input
        this.fileInput.value = '';
    }
    
    handleSendMessage() {
        const message = this.chatInput.textContent.trim();
        if (message) {
            this.addUserMessage(message);
            this.chatInput.textContent = '';
            
            // Simulate bot response for text messages
            setTimeout(() => {
                this.addBotMessage("I'm primarily designed to analyze images. Try uploading an image using the + button!");
            }, 1000);
        }
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addUserFileMessage(file) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        
        if (file.type.match('image.*')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <p>Uploaded image:</p>
                        <img src="${e.target.result}" alt="Uploaded image" class="upload-preview">
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>Uploaded video:</p>
                    <div class="uploaded-file">
                        <div class="file-icon">🎥</div>
                        <div class="file-info">
                            <div class="file-name">${this.escapeHtml(file.name)}</div>
                            <div class="file-size">${this.formatFileSize(file.size)}</div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(message, isHTML = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        if (isHTML) {
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${message}
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <p>${this.escapeHtml(message)}</p>
                </div>
            `;
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    async analyzeImage(file) {
        // Show loading message
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'message bot-message';
        loadingMessage.innerHTML = `
            <div class="message-content">
                <p>Analyzing image... <span class="loading"></span></p>
            </div>
        `;
        this.chatMessages.appendChild(loadingMessage);
        this.scrollToBottom();
        
        try {
            const result = await API.analyzeImage(file);
            
            // Remove loading message
            loadingMessage.remove();
            
            // Show result
            const resultClass = result.prediction === 'REAL' ? 'prediction-real' : 'prediction-fake';
            this.addBotMessage(`
                <p>Analysis complete!</p>
                <div class="prediction-result ${resultClass}">
                    Prediction: <strong>${result.prediction}</strong>
                </div>
                <p style="margin-top: 8px; font-size: 0.9rem; color: #64748b;">
                    The model thinks this image is ${result.prediction === 'REAL' ? 'authentic' : 'AI-generated or manipulated'}.
                </p>
            `, true);
            
        } catch (error) {
            // Remove loading message
            loadingMessage.remove();
            
            this.addBotMessage(`Sorry, there was an error analyzing the image: ${error.message}`);
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatUI();
});